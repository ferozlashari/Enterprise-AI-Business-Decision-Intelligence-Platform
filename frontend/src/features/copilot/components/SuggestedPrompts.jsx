
// =========================================================
// Enterprise AI Business Intelligence Platform
// Suggested Prompts
// =========================================================

const SUGGESTIONS = [

    "What are our top performing product categories?",

    "Which regions show declining sales?",

    "Summarize current inventory risk.",

    "What should we prioritize this quarter?",

];


// =========================================================
// COMPONENT
// =========================================================

export default function SuggestedPrompts({
    onSelect,
}) {

    const handleSelect = (suggestion) => {

        if (
            typeof onSelect !== "function"
        ) {

            return;

        }


        onSelect(suggestion);

    };


    return (

        <section
            className="
                px-5
                pb-3
                flex
                flex-wrap
                gap-2
            "
            aria-label="Suggested Copilot questions"
        >

            {SUGGESTIONS.map(
                (suggestion) => (

                    <button
                        key={suggestion}
                        type="button"
                        onClick={() =>
                            handleSelect(
                                suggestion
                            )
                        }
                        className="
                            text-xs
                            text-slate-300
                            bg-slate-800
                            hover:bg-slate-700
                            border
                            border-slate-700
                            rounded-full
                            px-3
                            py-1.5
                            transition
                            hover:text-white
                            focus:outline-none
                            focus:ring-2
                            focus:ring-blue-500/50
                        "
                    >

                        {suggestion}

                    </button>

                )
            )}

        </section>

    );

}

