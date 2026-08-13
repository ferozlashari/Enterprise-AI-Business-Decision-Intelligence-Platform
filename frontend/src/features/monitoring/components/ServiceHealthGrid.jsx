import { CheckCircle2, XCircle } from "lucide-react";


export default function ServiceHealthGrid({ services }) {

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

            <h2 className="text-white font-bold text-xl mb-4">
                Service Health
            </h2>

            <div
                className="
                    grid
                    grid-cols-1
                    sm:grid-cols-2
                    lg:grid-cols-3
                    gap-3
                "
            >

                {services.map((service) => {

                    const isHealthy = service.status === "Healthy";

                    return (

                        <div
                            key={service.name}
                            className="
                                flex
                                items-center
                                justify-between
                                bg-slate-800/50
                                border
                                border-slate-800
                                rounded-lg
                                px-4
                                py-3
                            "
                        >
                            <span className="text-sm text-slate-200 font-medium">
                                {service.name}
                            </span>

                            <span
                                className={`
                                    flex
                                    items-center
                                    gap-1.5
                                    text-xs
                                    font-semibold
                                    px-2.5
                                    py-1
                                    rounded-full
                                    ${
                                        isHealthy
                                            ? "bg-emerald-500/10 text-emerald-400"
                                            : "bg-red-500/10 text-red-400"
                                    }
                                `}
                            >
                                {isHealthy ? (
                                    <CheckCircle2 size={12} />
                                ) : (
                                    <XCircle size={12} />
                                )}
                                {service.status}
                            </span>

                        </div>

                    );

                })}

            </div>

        </div>
    );

}
