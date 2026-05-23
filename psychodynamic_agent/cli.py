import argparse

from psychodynamic_agent.config import get_settings
from psychodynamic_agent.llm import OpenAIResponsesClient
from psychodynamic_agent.orchestrator.memory import InMemoryConversation
from psychodynamic_agent.orchestrator.pipeline import PsychodynamicPipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("message", type=str)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    llm = OpenAIResponsesClient(api_key=settings.openai_api_key)
    memory = InMemoryConversation()
    pipeline = PsychodynamicPipeline(
        llm_client=llm,
        model_internal=settings.openai_model_internal,
        model_main=settings.openai_model_main,
        sealed_ultimate_need=settings.ultimate_need_seed,
    )
    state = memory.build_state(args.message)
    out = pipeline.run(state, debug=args.debug)
    print(out["final_response"])
    if args.debug:
        print("\n--- SAFE DEBUG TRACE ---")
        print(out["safe_debug_trace"])


if __name__ == "__main__":
    main()
