# BATCH 08D-06X - CHANGED-BOUNDARY SEMANTIC ADJUDICATION

baseline_head: 78ea6e489b2ddcb87536036574668207ef4dd3bb
final_amendment_mechanisms: 121
preserved_semantics: 113
changed_boundaries_adjudicated: 8

## Changed boundaries

US-CM-000246 | US-AM-MECH-UNIT-000012 | ELECTOR-MEETING-VOTING | family=F3 | scope=UNITED-STATES/PRESIDENTIAL-ELECTION/ELECTORS/MEETING-VOTING
normalized: The Constitution establishes this scoped procedural rule: Electors shall meet in their respective states and vote by ballot for President and Vice-President.
negative: The elector meeting and voting procedure is not established outside the source-defined actors, offices, ballot method, and respective-state setting.
basis: The meeting-and-voting duty is independently operative from the same-state inhabitancy constraint contained in the same prior child atom.

US-CM-000247 | US-AM-MECH-UNIT-000012 | ELECTOR-SAME-STATE-INHABITANCY-CONSTRAINT | family=F5 | scope=UNITED-STATES/PRESIDENTIAL-ELECTION/ELECTORS/MEETING-VOTING
normalized: The Constitution establishes this negative constraint: at least one of the persons voted for as President and Vice-President shall not be an inhabitant of the same state as the electors.
negative: An elector slate is not constitutionally established under this mechanism if both persons voted for are inhabitants of the same state as the electors.
basis: The inhabitancy restriction is a distinct negative constraint embedded within the prior combined elector-voting boundary.

US-CM-000260 | US-AM-MECH-UNIT-000012 | SENATE-CONTINGENT-SELECTION | family=F3 | scope=UNITED-STATES/PRESIDENTIAL-ELECTION/SENATE/CONTINGENT-SELECTION
normalized: The Constitution establishes this scoped selection procedure: if no person has a majority for Vice-President, the Senate shall choose the Vice-President from the two highest numbers on the list.
negative: The Senate contingent-selection procedure is not established unless no person has the required majority and the selection is confined to the two highest numbers on the Vice-Presidential list.
basis: Selection authority is independently operative from the quorum and majority thresholds previously combined in the same source child.

US-CM-000261 | US-AM-MECH-UNIT-000012 | SENATE-QUORUM | family=F4 | scope=UNITED-STATES/PRESIDENTIAL-ELECTION/SENATE/CONTINGENT-SELECTION
normalized: The Constitution establishes this quorum rule: a quorum for the Senate's contingent choice of Vice-President shall consist of two-thirds of the whole number of Senators.
negative: The Senate contingent Vice-Presidential choice is not established under this quorum mechanism when fewer than two-thirds of the whole number of Senators constitute the quorum.
basis: The source independently states a Senate quorum threshold within the prior combined contingent-election boundary.

US-CM-000262 | US-AM-MECH-UNIT-000012 | SENATE-MAJORITY | family=F4 | scope=UNITED-STATES/PRESIDENTIAL-ELECTION/SENATE/CONTINGENT-SELECTION
normalized: The Constitution establishes this concurrence threshold: a majority of the whole number of Senators is necessary to choose the Vice-President in the Senate contingent procedure.
negative: The Senate contingent Vice-Presidential choice is not established under this threshold mechanism without a majority of the whole number of Senators.
basis: The source independently states a Senate decision threshold separate from the contingent-selection authority and quorum.

US-CM-000290 | US-AM-MECH-UNIT-000026 | INTOXICATING-LIQUOR-PROHIBITED-OPERATIONS | family=F5 | scope=UNITED-STATES/INTOXICATING-LIQUOR/PROHIBITED-OPERATIONS
normalized: The Constitution establishes this prohibition: after one year from ratification, the manufacture, sale, or transportation of intoxicating liquors within, and the importation into or exportation from, the United States and territory subject to its jurisdiction for beverage purposes is prohibited.
negative: The prohibited-operation effect is not established outside the source-defined one-year effectiveness trigger, intoxicating-liquor subject, beverage-purpose limitation, enumerated operations, and territorial scope.
basis: Five lexical child atoms enumerate operation classes governed by one shared prohibition, timing rule, purpose limitation, and territorial scope.

US-CM-000327 | US-AM-MECH-UNIT-000050 | PRESIDENT-NO-INABILITY-DECLARATION-RESUMPTION | family=F1 | scope=UNITED-STATES/PRESIDENCY/INABILITY/RESUMPTION-COUNTERDECLARATION
normalized: The Constitution establishes this office-authority transition rule: when the President transmits the specified written declaration that no inability exists, the President resumes the powers and duties of the office, subject to the source-defined counterdeclaration condition.
negative: Presidential resumption is not established under this mechanism without the specified written declaration, recipients, and absence of the source-defined timely counterdeclaration.
basis: Presidential declaration and resumption form an independently operative authority transition within the prior combined Section 4 boundary.

US-CM-000328 | US-AM-MECH-UNIT-000050 | VP-MAJORITY-COUNTERDECLARATION-WINDOW | family=F4 | scope=UNITED-STATES/PRESIDENCY/INABILITY/RESUMPTION-COUNTERDECLARATION
normalized: The Constitution establishes this concurrence and timing rule: the Vice President and a majority of either the principal officers of the executive department or another body provided by Congress may transmit within four days the specified written declaration that the President is unable to discharge the powers and duties of the office.
negative: The counterdeclaration effect is not established under this mechanism without the Vice President, the required majority body, the specified written declaration and recipients, and transmission within the four-day window.
basis: The Vice-President-plus-majority counterdeclaration authority and four-day window are independently testable from the President's declaration and resumption effect.

SOURCE != INTERPRETATION
MECHANISM != PREDICATE
MECHANISM != ORYNTH CORRESPONDENCE

No predicates generated.
No ORYNTH correspondence assessed.
Canonical mechanism registry not rewritten.

NEXT: BATCH 08D-06Y - SUPERSEDING CANONICAL REGISTRY RECONCILIATION
