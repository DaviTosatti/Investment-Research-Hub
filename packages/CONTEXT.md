# Contexto de `packages/`

**Escopo:** código reutilizável sem processo próprio.

## O que existe hoje

- [x] [`engines/`](engines/CONTEXT.md) — pacote Python `hub_finance`

## Padrões

Rust/Julia só entram como pacote após benefício, equivalência numérica e distribuição medidos ([docs/COMPUTE_ARCHITECTURE.md](../docs/COMPUTE_ARCHITECTURE.md)).

## Ao fim das etapas

- [ ] **Etapa 2:** decisão documentada (adotar ou manter base) por motor acelerável.
- [ ] Nenhum crate/módulo vazio.
