# Historical profile oracle

`potterbot-xl-1.3.0.toml` is copied byte-for-byte from
`086a62a85f4716a1290842a5d507755a1e8bd6f5:src/clayline/profiles/potterbot-xl.toml`
(2026-08-02). It is used only to audit historical acceptance artifacts.

The production profile remains v1.4.0. Commit
`2dd3295c5d700f517c00d837386742a004dc2255` (2026-08-15) restored its reference
E3000 start charge after the E100 change proved unsupported. Tests compare
historical artifacts with v1.3.0 and current outputs with v1.4.0; they never
substitute the old charge into production output or rewrite old evidence.
