
import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    Loader2,
    RefreshCcw,
} from "lucide-react";

import {
    fetchCustomerSegments,
} from "./customer.api";

import CustomerStats from "./components/CustomerStats";
import SegmentPieChart from "./components/SegmentPieChart";
import CustomerTable from "./components/CustomerTable";


export default function Customer() {

    const [segments, setSegments] = useState(null);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState(null);


    // =====================================================
    // LOAD CUSTOMER SEGMENTATION
    // =====================================================

    useEffect(() => {

        loadCustomers();

    }, []);


    const loadCustomers = async () => {

        try {

            setLoading(true);

            setError(null);


            const result =
                await fetchCustomerSegments();


            console.log(
                "CUSTOMER SEGMENTATION RAW RESPONSE:",
                result
            );


            /*
             * Supported backend response formats:
             *
             * 1.
             * {
             *     status: "success",
             *     customers: 200,
             *     customer_segments: [...]
             * }
             *
             * 2.
             * {
             *     success: true,
             *     data: {
             *         customer_segments: [...]
             *     }
             * }
             *
             * 3.
             * {
             *     success: true,
             *     customer: {
             *         customer_segments: [...]
             *     }
             * }
             */


            let normalizedResult = result;


            if (
                result?.data &&
                typeof result.data === "object" &&
                !Array.isArray(result.data)
            ) {

                normalizedResult = {
                    ...result.data,

                    success:
                        result?.success ??
                        result?.data?.success,

                };

            }


            if (
                result?.customer &&
                typeof result.customer === "object"
            ) {

                normalizedResult = {
                    ...result.customer,

                    success:
                        result?.success ??
                        result?.customer?.success,

                };

            }


            if (
                result?.customer_segments &&
                typeof result.customer_segments === "object" &&
                !Array.isArray(result.customer_segments)
            ) {

                /*
                 * Handles a wrapper such as:
                 *
                 * {
                 *     customer_segments: {
                 *         customers: ...,
                 *         customer_segments: [...]
                 *     }
                 * }
                 */

                normalizedResult =
                    result.customer_segments;

            }


            console.log(
                "NORMALIZED CUSTOMER RESPONSE:",
                normalizedResult
            );


            setSegments(
                normalizedResult
            );


        } catch (err) {

            console.error(
                "CUSTOMER SEGMENTATION ERROR:",
                err
            );


            const detail =
                err?.response?.data?.detail;


            if (
                Array.isArray(detail)
            ) {

                setError(
                    detail
                        .map(
                            item =>
                                item?.msg ||
                                String(item)
                        )
                        .join(", ")
                );

            }

            else if (
                typeof detail === "string"
            ) {

                setError(detail);

            }

            else {

                setError(
                    err?.message ||
                    "Unable to load customer intelligence."
                );

            }

        } finally {

            setLoading(false);

        }

    };


    // =====================================================
    // NORMALIZE SEGMENT DATA
    // =====================================================

    const segmentData = useMemo(() => {

        if (!segments) {

            return [];

        }


        /*
         * Your PredictionService returns:
         *
         * customer_segments: [...]
         *
         * So we check that first.
         */


        let rawSegments = [];


        if (
            Array.isArray(
                segments.customer_segments
            )
        ) {

            rawSegments =
                segments.customer_segments;

        }

        else if (
            Array.isArray(
                segments.segments
            )
        ) {

            rawSegments =
                segments.segments;

        }

        else if (
            Array.isArray(
                segments.clusters
            )
        ) {

            rawSegments =
                segments.clusters;

        }


        /*
         * Some APIs may return:
         *
         * clusters: {
         *     "0": 50,
         *     "1": 75,
         *     "2": 40
         * }
         *
         * Convert that object into an array.
         */


        if (
            rawSegments.length === 0 &&
            segments.clusters &&
            typeof segments.clusters === "object" &&
            !Array.isArray(segments.clusters)
        ) {

            rawSegments =
                Object.entries(
                    segments.clusters
                ).map(
                    ([cluster, customers]) => ({

                        cluster,

                        customers,

                    })
                );

        }


        /*
         * Same fallback for:
         *
         * segments: {
         *     "0": 50,
         *     "1": 75
         * }
         */


        if (
            rawSegments.length === 0 &&
            segments.segments &&
            typeof segments.segments === "object" &&
            !Array.isArray(segments.segments)
        ) {

            rawSegments =
                Object.entries(
                    segments.segments
                ).map(
                    ([cluster, customers]) => ({

                        cluster,

                        customers,

                    })
                );

        }


        return rawSegments
            .filter(
                item =>
                    item !== null &&
                    typeof item === "object"
            )
            .map(
                (item, index) => {

                    const clusterValue =
                        item?.cluster ??
                        item?.cluster_id ??
                        item?.clusterId ??
                        item?.segment ??
                        index;


                    const customersValue =
                        item?.customers ??
                        item?.customer_count ??
                        item?.count ??
                        item?.value ??
                        0;


                    const averageAge =
                        item?.average_age ??
                        item?.avg_age ??
                        item?.age ??
                        0;


                    const averageIncome =
                        item?.average_income ??
                        item?.avg_income ??
                        item?.income ??
                        0;


                    const averageSpending =
                        item?.average_spending_score ??
                        item?.avg_spending_score ??
                        item?.spending_score ??
                        item?.spending ??
                        0;


                    let clusterNumber =
                        Number(
                            clusterValue
                        );


                    if (
                        !Number.isFinite(
                            clusterNumber
                        )
                    ) {

                        clusterNumber =
                            index;

                    }


                    return {

                        cluster:
                            clusterNumber,

                        customers:
                            Number(
                                customersValue
                            ) || 0,

                        average_age:
                            Number(
                                averageAge
                            ) || 0,

                        average_income:
                            Number(
                                averageIncome
                            ) || 0,

                        average_spending_score:
                            Number(
                                averageSpending
                            ) || 0,

                    };

                }
            );

    }, [segments]);


    // =====================================================
    // PIE CHART DATA
    // =====================================================

    const pieData = useMemo(() => {

        return segmentData.map(
            (item) => ({

                name:
                    `Cluster ${item.cluster}`,

                value:
                    item.customers,

            })
        );

    }, [segmentData]);


    // =====================================================
    // LARGEST SEGMENT
    // =====================================================

    const largestSegment = useMemo(() => {

        if (
            segmentData.length === 0
        ) {

            return null;

        }


        const largest =
            segmentData.reduce(
                (max, item) => {

                    return (
                        item.customers >
                        max.customers
                    )
                        ? item
                        : max;

                },
                segmentData[0]
            );


        return {

            name:
                `Cluster ${largest.cluster}`,

            value:
                largest.customers,

        };

    }, [segmentData]);


    // =====================================================
    // HIGHEST SPENDING SEGMENT
    // =====================================================

    const highestSpendingSegment =
        useMemo(() => {

            if (
                segmentData.length === 0
            ) {

                return null;

            }


            const highest =
                segmentData.reduce(
                    (max, item) => {

                        return (
                            item.average_spending_score >
                            max.average_spending_score
                        )
                            ? item
                            : max;

                    },
                    segmentData[0]
                );


            return {

                name:
                    `Cluster ${highest.cluster}`,

                score:
                    highest.average_spending_score,

                customers:
                    highest.customers,

            };

        }, [segmentData]);


    // =====================================================
    // TOTAL CUSTOMERS
    // =====================================================

    const totalCustomers = useMemo(() => {

        const backendTotal =
            Number(
                segments?.customers
            );


        if (
            Number.isFinite(
                backendTotal
            ) &&
            backendTotal > 0
        ) {

            return backendTotal;

        }


        return segmentData.reduce(
            (total, item) =>
                total + item.customers,
            0
        );

    }, [
        segments,
        segmentData,
    ]);


    // =====================================================
    // SEGMENT COUNT
    // =====================================================

    const segmentCount = useMemo(() => {

        const backendCount =
            Number(
                segments?.segment_count
            );


        if (
            Number.isFinite(
                backendCount
            ) &&
            backendCount >= 0
        ) {

            return backendCount;

        }


        return segmentData.length;

    }, [
        segments,
        segmentData,
    ]);


    // =====================================================
    // LOADING
    // =====================================================

    if (loading) {

        return (

            <div className="
                min-h-[70vh]
                flex
                items-center
                justify-center
                text-white
            ">

                <div className="
                    bg-slate-900
                    border
                    border-slate-800
                    rounded-xl
                    px-6
                    py-5
                    flex
                    items-center
                    gap-3
                    text-slate-300
                ">

                    <Loader2
                        size={20}
                        className="animate-spin"
                    />

                    Loading customer intelligence...

                </div>

            </div>

        );

    }


    // =====================================================
    // MAIN
    // =====================================================

    return (

        <div className="
            p-6
            text-white
            space-y-6
        ">


            {/* ==========================================
                HEADER
            ========================================== */}

            <div className="
                flex
                flex-col
                md:flex-row
                md:items-center
                md:justify-between
                gap-4
            ">

                <div>

                    <h1 className="
                        text-3xl
                        font-bold
                    ">

                        Customer Intelligence

                    </h1>


                    <p className="
                        text-slate-400
                        mt-1
                    ">

                        Segmentation clusters derived
                        from customer demographics and
                        spending behavior.

                    </p>

                </div>


                <button
                    onClick={loadCustomers}
                    disabled={loading}
                    className="
                        flex
                        items-center
                        justify-center
                        gap-2
                        bg-blue-600
                        hover:bg-blue-700
                        disabled:opacity-50
                        disabled:cursor-not-allowed
                        px-4
                        py-2
                        rounded-lg
                        font-semibold
                        transition
                    "
                >

                    <RefreshCcw size={18} />

                    Refresh

                </button>

            </div>


            {/* ==========================================
                ERROR
            ========================================== */}

            {error && (

                <div className="
                    bg-red-500/10
                    border
                    border-red-500/30
                    text-red-400
                    rounded-lg
                    px-4
                    py-3
                    text-sm
                ">

                    {error}

                </div>

            )}


            {/* ==========================================
                DATA STATUS
            ========================================== */}

            {!error &&
                segmentData.length === 0 && (

                <div className="
                    bg-yellow-500/10
                    border
                    border-yellow-500/30
                    text-yellow-400
                    rounded-lg
                    px-4
                    py-3
                    text-sm
                ">

                    Customer segmentation data is
                    currently unavailable.

                </div>

            )}


            {/* ==========================================
                KPI CARDS
            ========================================== */}

            <CustomerStats

                totalCustomers={
                    totalCustomers
                }

                segmentCount={
                    segmentCount
                }

                largestSegment={
                    largestSegment
                }

                highestSpendingSegment={
                    highestSpendingSegment
                }

            />


            {/* ==========================================
                CHART + SEGMENT TABLE
            ========================================== */}

            <div className="
                grid
                grid-cols-1
                xl:grid-cols-2
                gap-6
            ">


                <SegmentPieChart
                    data={pieData}
                />


                <CustomerTable
                    customers={segmentData}
                />


            </div>


            {/* ==========================================
                DETAILED SEGMENT ANALYSIS
            ========================================== */}

            <div className="
                bg-slate-900
                border
                border-slate-800
                rounded-xl
                p-5
            ">

                <div className="mb-4">

                    <h2 className="
                        text-xl
                        font-bold
                        text-white
                    ">

                        Customer Segment Details

                    </h2>


                    <p className="
                        text-sm
                        text-slate-400
                        mt-1
                    ">

                        K-Means cluster characteristics

                    </p>

                </div>


                {segmentData.length === 0 ? (

                    <p className="
                        text-slate-500
                        text-sm
                        text-center
                        py-10
                    ">

                        No segmentation details available.

                    </p>

                ) : (

                    <div className="overflow-x-auto">

                        <table className="
                            w-full
                            text-sm
                            text-left
                        ">

                            <thead>

                                <tr className="
                                    text-slate-400
                                    border-b
                                    border-slate-800
                                ">

                                    <th className="
                                        py-3
                                        pr-4
                                    ">

                                        Cluster

                                    </th>


                                    <th className="
                                        py-3
                                        pr-4
                                    ">

                                        Customers

                                    </th>


                                    <th className="
                                        py-3
                                        pr-4
                                    ">

                                        Avg Age

                                    </th>


                                    <th className="
                                        py-3
                                        pr-4
                                    ">

                                        Avg Income

                                    </th>


                                    <th className="
                                        py-3
                                    ">

                                        Avg Spending Score

                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {segmentData.map(
                                    (item) => (

                                        <tr
                                            key={
                                                `cluster-${item.cluster}`
                                            }
                                            className="
                                                border-b
                                                border-slate-800/60
                                                hover:bg-slate-800/30
                                                transition
                                            "
                                        >

                                            <td className="
                                                py-3
                                                pr-4
                                                font-semibold
                                                text-white
                                            ">

                                                Cluster{" "}

                                                {
                                                    item.cluster
                                                }

                                            </td>


                                            <td className="
                                                py-3
                                                pr-4
                                                text-slate-300
                                            ">

                                                {
                                                    item.customers
                                                }

                                            </td>


                                            <td className="
                                                py-3
                                                pr-4
                                                text-slate-300
                                            ">

                                                {
                                                    item.average_age.toFixed(
                                                        2
                                                    )
                                                }

                                            </td>


                                            <td className="
                                                py-3
                                                pr-4
                                                text-slate-300
                                            ">

                                                {
                                                    item.average_income.toFixed(
                                                        2
                                                    )
                                                }k

                                            </td>


                                            <td className="
                                                py-3
                                                font-semibold
                                                text-white
                                            ">

                                                {
                                                    item.average_spending_score.toFixed(
                                                        2
                                                    )
                                                }

                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    </div>

                )}

            </div>


        </div>

    );

}

