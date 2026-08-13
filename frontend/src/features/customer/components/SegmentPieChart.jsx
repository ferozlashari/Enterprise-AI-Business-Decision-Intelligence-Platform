
import {
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend,
} from "recharts";

const COLORS = [
    "#3b82f6",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#a855f7",
    "#14b8a6",
];


// =====================================================
// TOOLTIP
// (module scope so it isn't recreated every render;
// receives `total` as a prop instead of closing over it)
// =====================================================

const CustomTooltip = ({
    active,
    payload,
    total,
}) => {

    if (
        !active ||
        !Array.isArray(payload) ||
        payload.length === 0
    ) {
        return null;
    }


    const item =
        payload[0]?.payload;


    if (!item) {
        return null;
    }


    const value =
        Number(item.value) || 0;


    const percentage =
        total > 0
            ? (
                value /
                total *
                100
            )
            : 0;


    return (

        <div
            className="
                bg-slate-950
                border
                border-slate-700
                rounded-lg
                px-4
                py-3
                shadow-xl
            "
        >

            <p
                className="
                    text-white
                    font-semibold
                "
            >
                {item.name}
            </p>


            <p
                className="
                    text-slate-300
                    text-sm
                    mt-1
                "
            >
                Customers:{" "}
                {value.toLocaleString()}
            </p>


            <p
                className="
                    text-slate-400
                    text-sm
                "
            >
                Distribution:{" "}
                {percentage.toFixed(1)}%
            </p>

        </div>

    );
};


export default function SegmentPieChart({
    data = [],
}) {

    // =====================================================
    // SAFE + NORMALIZED DATA
    // =====================================================

    const safeData = Array.isArray(data)
        ? data
            .map((item, index) => {

                const value =
                    Number(item?.value);

                return {
                    name:
                        typeof item?.name === "string" &&
                        item.name.trim()
                            ? item.name.trim()
                            : `Cluster ${index}`,

                    value:
                        Number.isFinite(value)
                            ? value
                            : 0,
                };

            })
            .filter(
                (item) =>
                    item.value > 0
            )
        : [];


    // =====================================================
    // TOTAL CUSTOMERS
    // =====================================================

    const total = safeData.reduce(
        (sum, item) =>
            sum + item.value,
        0
    );


    // =====================================================
    // EMPTY STATE
    // =====================================================

    if (
        safeData.length === 0
    ) {

        return (

            <div
                className="
                    bg-slate-900
                    border
                    border-slate-800
                    rounded-xl
                    p-5
                "
            >

                <h2
                    className="
                        text-white
                        font-bold
                        text-xl
                        mb-4
                    "
                >
                    Segment Distribution
                </h2>


                <p
                    className="
                        text-slate-500
                        text-sm
                        text-center
                        py-10
                    "
                >
                    No segmentation data available yet.
                </p>

            </div>

        );
    }


    // =====================================================
    // MAIN
    // =====================================================

    return (

        <div
            className="
                bg-slate-900
                border
                border-slate-800
                rounded-xl
                p-5
            "
        >

            {/* =================================================
                HEADER
            ================================================= */}

            <div className="mb-4">

                <h2
                    className="
                        text-white
                        font-bold
                        text-xl
                    "
                >
                    Segment Distribution
                </h2>


                <p
                    className="
                        text-slate-400
                        text-sm
                        mt-1
                    "
                >
                    Customer distribution across
                    K-Means segments.
                </p>

            </div>


            {/* =================================================
                PIE CHART
            ================================================= */}

            <div
                style={{
                    width: "100%",
                    height: 320,
                }}
            >

                <ResponsiveContainer
                    width="100%"
                    height="100%"
                >

                    <PieChart>

                        <Pie
                            data={safeData}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="45%"
                            outerRadius={100}
                            innerRadius={45}
                            paddingAngle={2}
                            label={false}
                            labelLine={false}
                            isAnimationActive={true}
                        >

                            {safeData.map(
                                (entry, index) => (

                                    <Cell
                                        key={
                                            `${entry.name}-${index}`
                                        }
                                        fill={
                                            COLORS[
                                                index %
                                                COLORS.length
                                            ]
                                        }
                                    />

                                )
                            )}

                        </Pie>


                        {/* =================================================
                            TOOLTIP
                        ================================================= */}

                        <Tooltip
                            content={
                                <CustomTooltip total={total} />
                            }
                        />


                        {/* =================================================
                            LEGEND
                        ================================================= */}

                        <Legend
                            verticalAlign="bottom"
                            align="center"
                            iconType="circle"
                            formatter={(value) => (

                                <span
                                    className="
                                        text-slate-300
                                        text-sm
                                    "
                                >
                                    {value}
                                </span>

                            )}
                        />

                    </PieChart>

                </ResponsiveContainer>

            </div>


            {/* =================================================
                SEGMENT SUMMARY
            ================================================= */}

            <div
                className="
                    mt-4
                    grid
                    grid-cols-2
                    sm:grid-cols-3
                    lg:grid-cols-5
                    gap-2
                "
            >

                {safeData.map(
                    (item, index) => {

                        const percentage =
                            total > 0
                                ? (
                                    item.value /
                                    total
                                ) *
                                100
                                : 0;


                        return (

                            <div
                                key={
                                    `${item.name}-summary-${index}`
                                }
                                className="
                                    bg-slate-950
                                    border
                                    border-slate-800
                                    rounded-lg
                                    px-3
                                    py-2
                                "
                            >

                                <div
                                    className="
                                        flex
                                        items-center
                                        gap-2
                                    "
                                >

                                    <span
                                        className="
                                            w-2.5
                                            h-2.5
                                            rounded-full
                                            shrink-0
                                        "
                                        style={{
                                            backgroundColor:
                                                COLORS[
                                                    index %
                                                    COLORS.length
                                                ],
                                        }}
                                    />


                                    <span
                                        className="
                                            text-slate-300
                                            text-xs
                                            truncate
                                        "
                                    >
                                        {item.name}
                                    </span>

                                </div>


                                <div
                                    className="
                                        mt-1
                                        text-white
                                        font-semibold
                                    "
                                >
                                    {item.value.toLocaleString()}
                                </div>


                                <div
                                    className="
                                        text-slate-500
                                        text-xs
                                    "
                                >
                                    {percentage.toFixed(1)}%
                                </div>

                            </div>

                        );

                    }
                )}

            </div>

        </div>

    );
}

