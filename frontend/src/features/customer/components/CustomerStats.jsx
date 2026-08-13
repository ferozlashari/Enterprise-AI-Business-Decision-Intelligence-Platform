
import {
    Users,
    Layers,
    UserCheck,
    TrendingUp,
} from "lucide-react";


export default function CustomerStats({

    totalCustomers,

    segmentCount,

    largestSegment,

    highestSpendingSegment,

}) {

    return (

        <div className="
            grid
            grid-cols-1
            sm:grid-cols-2
            xl:grid-cols-4
            gap-4
        ">


            {/* ==========================================
                TOTAL CUSTOMERS
            ========================================== */}

            <div className="
                bg-slate-900
                border
                border-slate-800
                rounded-xl
                p-5
            ">

                <div className="
                    flex
                    items-center
                    gap-2
                    text-slate-400
                    text-sm
                    mb-1
                ">

                    <Users size={16} />

                    Total Customers

                </div>


                <p className="
                    text-2xl
                    font-bold
                    text-white
                ">

                    {Number(
                        totalCustomers ?? 0
                    ).toLocaleString()}

                </p>

            </div>


            {/* ==========================================
                SEGMENTS
            ========================================== */}

            <div className="
                bg-slate-900
                border
                border-slate-800
                rounded-xl
                p-5
            ">

                <div className="
                    flex
                    items-center
                    gap-2
                    text-slate-400
                    text-sm
                    mb-1
                ">

                    <Layers size={16} />

                    Segments Identified

                </div>


                <p className="
                    text-2xl
                    font-bold
                    text-white
                ">

                    {Number(
                        segmentCount ?? 0
                    )}

                </p>

            </div>


            {/* ==========================================
                LARGEST SEGMENT
            ========================================== */}

            <div className="
                bg-slate-900
                border
                border-slate-800
                rounded-xl
                p-5
            ">

                <div className="
                    flex
                    items-center
                    gap-2
                    text-slate-400
                    text-sm
                    mb-1
                ">

                    <UserCheck size={16} />

                    Largest Segment

                </div>


                <p className="
                    text-xl
                    font-bold
                    text-white
                    truncate
                ">

                    {largestSegment?.name ?? "—"}

                </p>


                {largestSegment?.value != null && (

                    <p className="
                        text-xs
                        text-slate-500
                        mt-1
                    ">

                        {Number(
                            largestSegment.value
                        ).toLocaleString()} customers

                    </p>

                )}

            </div>


            {/* ==========================================
                HIGHEST SPENDING SEGMENT
            ========================================== */}

            <div className="
                bg-slate-900
                border
                border-slate-800
                rounded-xl
                p-5
            ">

                <div className="
                    flex
                    items-center
                    gap-2
                    text-slate-400
                    text-sm
                    mb-1
                ">

                    <TrendingUp size={16} />

                    Highest Spending

                </div>


                <p className="
                    text-xl
                    font-bold
                    text-white
                    truncate
                ">

                    {highestSpendingSegment?.name ?? "—"}

                </p>


                {highestSpendingSegment?.score != null && (

                    <p className="
                        text-xs
                        text-slate-500
                        mt-1
                    ">

                        Spending Score:{" "}

                        {Number(
                            highestSpendingSegment.score
                        ).toFixed(2)}

                    </p>

                )}

            </div>

        </div>

    );

}

