# Swift implementation reference

Use this as a starting shape, not as a mandatory file layout. Keep the engine
platform-agnostic: Foundation types only, no SwiftUI, no device APIs, and no
network access.

## Core types

```swift
import Foundation

enum ContentAgeBand: String, Codable, CaseIterable {
    case unknown, under13, age13to15, age16to17, adult

    var isMinor: Bool {
        switch self {
        case .under13, .age13to15, .age16to17: return true
        case .unknown, .adult: return false
        }
    }

    func isBelow(minimumAge: Int) -> Bool {
        switch self {
        case .unknown: return false
        case .under13: return minimumAge > 0
        case .age13to15: return minimumAge > 13
        case .age16to17: return minimumAge > 16
        case .adult: return minimumAge > 18
        }
    }
}

enum ContentAccountState: String, Codable {
    case guest, signedIn, restricted
}

enum ContentComplianceFlag: String, Codable, Hashable, CaseIterable {
    case legalBlock
    case ageVerificationRequired
    case limitedContentOnly
}

struct ContentPolicyContext: Equatable, Codable {
    var countryCode: String
    var ageBand: ContentAgeBand
    var accountState: ContentAccountState
    var complianceFlags: Set<ContentComplianceFlag>

    var normalizedCountryCode: String {
        countryCode.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
    }
}
```

## Decision types

```swift
enum ContentMode: String, Codable, CaseIterable {
    case full, limited, ageVerificationRequired, unavailable

    var severity: Int {
        switch self {
        case .full: return 0
        case .limited: return 1
        case .ageVerificationRequired: return 2
        case .unavailable: return 3
        }
    }
}

struct ContentPolicyReason: Identifiable, Equatable, Codable {
    enum Code: String, Codable, CaseIterable {
        case serverLegalBlock
        case blockedRegion
        case accountRestricted
        case serverAgeVerification
        case underMinimumAge
        case unknownAge
        case serverLimit
        case limitedRegion
        case minorContentLimit
        case unknownRegion
        case noRestriction
    }

    var code: Code
    var mode: ContentMode
    var id: String { code.rawValue }
}

struct ContentPolicyDecision: Equatable {
    var mode: ContentMode
    var reasons: [ContentPolicyReason]
    var policyVersion: String
    var evaluatedAt: Date
}
```

## Configuration

```swift
struct ContentPolicyConfiguration: Equatable {
    var policyVersion: String
    var minimumAge: Int
    var blockedCountryCodes: Set<String>
    var limitedCountryCodes: Set<String>
    var unknownRegionMode: ContentMode
    var requiresAgeVerificationForUnknownAge: Bool
    var minorsOnlySeeLimitedContent: Bool
}
```

Keep the configuration versioned and sourced from a documented policy. Do not
hard-code a block list without a legal or product reason.

## Gate

```swift
struct ContentPolicyGate {
    func evaluate(
        _ context: ContentPolicyContext,
        configuration: ContentPolicyConfiguration,
        now: Date = Date()
    ) -> ContentPolicyDecision {
        let country = context.normalizedCountryCode
        var reasons: [ContentPolicyReason] = []

        if context.complianceFlags.contains(.legalBlock) {
            reasons.append(.init(code: .serverLegalBlock, mode: .unavailable))
        }
        if !country.isEmpty, configuration.blockedCountryCodes.contains(country) {
            reasons.append(.init(code: .blockedRegion, mode: .unavailable))
        }
        if context.accountState == .restricted {
            reasons.append(.init(code: .accountRestricted, mode: .limited))
        }
        if context.complianceFlags.contains(.ageVerificationRequired) {
            reasons.append(.init(code: .serverAgeVerification, mode: .ageVerificationRequired))
        }
        if context.ageBand.isBelow(minimumAge: configuration.minimumAge) {
            reasons.append(.init(code: .underMinimumAge, mode: .ageVerificationRequired))
        }
        if context.ageBand == .unknown, configuration.requiresAgeVerificationForUnknownAge {
            reasons.append(.init(code: .unknownAge, mode: .ageVerificationRequired))
        }
        if context.complianceFlags.contains(.limitedContentOnly) {
            reasons.append(.init(code: .serverLimit, mode: .limited))
        }
        if !country.isEmpty, configuration.limitedCountryCodes.contains(country) {
            reasons.append(.init(code: .limitedRegion, mode: .limited))
        }
        if context.ageBand.isMinor, configuration.minorsOnlySeeLimitedContent {
            reasons.append(.init(code: .minorContentLimit, mode: .limited))
        }
        if country.isEmpty {
            reasons.append(.init(code: .unknownRegion, mode: configuration.unknownRegionMode))
        }
        if reasons.isEmpty {
            reasons.append(.init(code: .noRestriction, mode: .full))
        }

        let mode = reasons.map(\.mode).max { $0.severity < $1.severity } ?? .full
        return ContentPolicyDecision(
            mode: mode,
            reasons: reasons,
            policyVersion: configuration.policyVersion,
            evaluatedAt: now
        )
    }
}
```

## Audit log

```swift
struct ContentPolicyAuditEntry: Identifiable, Equatable, Codable {
    let id: UUID
    let evaluatedAt: Date
    let policyVersion: String
    let countryCode: String
    let ageBand: ContentAgeBand
    let accountState: ContentAccountState
    let complianceFlags: [ContentComplianceFlag]
    let mode: ContentMode
    let reasonCodes: [ContentPolicyReason.Code]
}

struct ContentPolicyAuditLog: Equatable {
    private(set) var entries: [ContentPolicyAuditEntry] = []
    let capacity: Int

    init(capacity: Int = 100) {
        self.capacity = max(1, capacity)
    }

    mutating func record(
        _ decision: ContentPolicyDecision,
        context: ContentPolicyContext,
        id: UUID = UUID()
    ) {
        entries.insert(
            ContentPolicyAuditEntry(
                id: id,
                evaluatedAt: decision.evaluatedAt,
                policyVersion: decision.policyVersion,
                countryCode: context.normalizedCountryCode,
                ageBand: context.ageBand,
                accountState: context.accountState,
                complianceFlags: context.complianceFlags.sorted { $0.rawValue < $1.rawValue },
                mode: decision.mode,
                reasonCodes: decision.reasons.map(\.code)
            ),
            at: 0
        )
        if entries.count > capacity {
            entries.removeLast(entries.count - capacity)
        }
    }
}
```

## Test matrix

| Case | Expected mode |
| --- | --- |
| No applicable rule | `full` |
| Server legal block | `unavailable` |
| Blocked region | `unavailable` |
| Restricted account | `limited` |
| Server age-verification flag | `ageVerificationRequired` |
| Age band below minimum | `ageVerificationRequired` |
| Unknown age, verification required | `ageVerificationRequired` |
| Server limited-content flag | `limited` |
| Limited region | `limited` |
| Minor account | `limited` |
| Unknown region | configuration fallback |
| Overlapping rules | most restrictive mode |

Also test: country-code normalization, stable output for the same inputs and
injected date, audit entries newest-first, audit capacity trimming, and that
changing a declared input in app state re-evaluates the decision.

## Integration checklist

- One `evaluate` call at the app-state boundary.
- One published decision consumed by every content surface.
- Context changes re-evaluate.
- Account changes update `ContentAccountState`.
- Default unknown inputs are explicit, not guessed.
- Audit log is bounded and contains only declared inputs and reason codes.
