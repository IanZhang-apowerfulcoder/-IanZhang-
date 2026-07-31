# Agent Modules

Each Agent exposes `async run(input, context) -> output` and must validate output against the assigned JSON Schema. Parallel Agent groups submit branch outputs to a coordinator; they never write the final business decision.
