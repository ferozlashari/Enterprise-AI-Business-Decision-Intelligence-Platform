
import api from "../../api/axios";


// =====================================================
// CUSTOMER SEGMENTATION
// =====================================================

export const fetchCustomerSegments = async () => {

    try {

        const response = await api.get(
            "/customer/segments"
        );

        const payload =
            response?.data ?? {};


        console.log(
            "RAW CUSTOMER API RESPONSE:",
            payload
        );


        /*
         * Supported backend response:
         *
         * {
         *     success: true,
         *
         *     segments: {
         *         status: "success",
         *         available: true,
         *         customers: 200,
         *         segments: {
         *             "0": 20,
         *             "1": 54
         *         },
         *         clusters: {
         *             "0": 20,
         *             "1": 54
         *         },
         *         customer_segments: [
         *             ...
         *         ],
         *         data: [
         *             ...
         *         ]
         *     }
         * }
         *
         *
         * Also supports:
         *
         * {
         *     customers: 200,
         *     customer_segments: [
         *         ...
         *     ]
         * }
         */


        // =================================================
        // FIND ACTUAL BACKEND DATA
        // =================================================

        let backend = {};


        if (
            payload?.segments &&
            typeof payload.segments === "object" &&
            !Array.isArray(payload.segments)
        ) {

            backend =
                payload.segments;

        }

        else if (
            payload?.data &&
            typeof payload.data === "object" &&
            !Array.isArray(payload.data)
        ) {

            backend =
                payload.data;

        }

        else {

            backend =
                payload;

        }


        console.log(
            "CUSTOMER BACKEND DATA:",
            backend
        );


        // =================================================
        // CUSTOMER COUNT
        // =================================================

        let customers =
            Number(
                backend?.customers
                ??
                backend?.total_customers
                ??
                backend?.customer_count
                ??
                0
            );


        if (
            !Number.isFinite(customers) ||
            customers < 0
        ) {

            customers = 0;

        }


        // =================================================
        // NORMALIZE SEGMENTS
        // =================================================

        let normalizedSegments = [];


        /*
         * Case 1:
         *
         * customer_segments: [
         *     {
         *         cluster: 0,
         *         customers: 20,
         *         average_age: 25,
         *         average_income: 50,
         *         average_spending_score: 70
         *     }
         * ]
         */

        if (
            Array.isArray(
                backend?.customer_segments
            )
        ) {

            normalizedSegments =
                backend.customer_segments.map(
                    (item, index) => {

                        const rawCluster =
                            item?.cluster
                            ??
                            item?.cluster_id
                            ??
                            item?.segment
                            ??
                            index;


                        const clusterText =
                            String(
                                rawCluster
                            );


                        const clusterMatch =
                            clusterText.match(
                                /\d+/
                            );


                        const cluster =
                            clusterMatch
                                ? Number(
                                    clusterMatch[0]
                                )
                                : index;


                        const customerCount =
                            Number(
                                item?.customers
                                ??
                                item?.count
                                ??
                                item?.value
                                ??
                                0
                            );


                        const averageAge =
                            Number(
                                item?.average_age
                                ??
                                item?.avg_age
                                ??
                                0
                            );


                        const averageIncome =
                            Number(
                                item?.average_income
                                ??
                                item?.avg_income
                                ??
                                0
                            );


                        const averageSpending =
                            Number(
                                item?.average_spending_score
                                ??
                                item?.spending_score
                                ??
                                item?.average_spending
                                ??
                                0
                            );


                        return {

                            cluster:
                                Number.isFinite(
                                    cluster
                                )
                                    ? cluster
                                    : index,

                            segment:
                                `Cluster ${
                                    Number.isFinite(
                                        cluster
                                    )
                                        ? cluster
                                        : index
                                }`,

                            name:
                                `Cluster ${
                                    Number.isFinite(
                                        cluster
                                    )
                                        ? cluster
                                        : index
                                }`,

                            customers:
                                Number.isFinite(
                                    customerCount
                                )
                                    ? customerCount
                                    : 0,

                            value:
                                Number.isFinite(
                                    customerCount
                                )
                                    ? customerCount
                                    : 0,

                            average_age:
                                Number.isFinite(
                                    averageAge
                                )
                                    ? averageAge
                                    : 0,

                            average_income:
                                Number.isFinite(
                                    averageIncome
                                )
                                    ? averageIncome
                                    : 0,

                            average_spending_score:
                                Number.isFinite(
                                    averageSpending
                                )
                                    ? averageSpending
                                    : 0,

                        };

                    }
                );

        }


        /*
         * Case 2:
         *
         * segments is already an array.
         *
         * This is useful if the backend later returns:
         *
         * segments: [
         *     ...
         * ]
         */

        else if (
            Array.isArray(
                backend?.segments
            )
        ) {

            normalizedSegments =
                backend.segments.map(
                    (item, index) => {

                        const rawCluster =
                            item?.cluster
                            ??
                            item?.cluster_id
                            ??
                            item?.segment
                            ??
                            index;


                        const clusterText =
                            String(
                                rawCluster
                            );


                        const clusterMatch =
                            clusterText.match(
                                /\d+/
                            );


                        const cluster =
                            clusterMatch
                                ? Number(
                                    clusterMatch[0]
                                )
                                : index;


                        return {

                            cluster:
                                Number.isFinite(
                                    cluster
                                )
                                    ? cluster
                                    : index,

                            segment:
                                `Cluster ${
                                    Number.isFinite(
                                        cluster
                                    )
                                        ? cluster
                                        : index
                                }`,

                            name:
                                `Cluster ${
                                    Number.isFinite(
                                        cluster
                                    )
                                        ? cluster
                                        : index
                                }`,

                            customers:
                                Number(
                                    item?.customers
                                    ??
                                    item?.count
                                    ??
                                    item?.value
                                    ??
                                    0
                                ) || 0,

                            value:
                                Number(
                                    item?.customers
                                    ??
                                    item?.count
                                    ??
                                    item?.value
                                    ??
                                    0
                                ) || 0,

                            average_age:
                                Number(
                                    item?.average_age
                                    ??
                                    0
                                ) || 0,

                            average_income:
                                Number(
                                    item?.average_income
                                    ??
                                    0
                                ) || 0,

                            average_spending_score:
                                Number(
                                    item?.average_spending_score
                                    ??
                                    0
                                ) || 0,

                        };

                    }
                );

        }


        /*
         * Case 3:
         *
         * segments object:
         *
         * {
         *     "0": 20,
         *     "1": 54,
         *     "2": 40
         * }
         */

        else if (
            backend?.segments &&
            typeof backend.segments === "object" &&
            !Array.isArray(
                backend.segments
            )
        ) {

            normalizedSegments =
                Object.entries(
                    backend.segments
                ).map(
                    ([cluster, count]) => {

                        const numericCluster =
                            Number(
                                String(
                                    cluster
                                ).match(
                                    /\d+/
                                )?.[0]
                            );


                        const customerCount =
                            Number(
                                count
                            );


                        return {

                            cluster:
                                Number.isFinite(
                                    numericCluster
                                )
                                    ? numericCluster
                                    : 0,

                            segment:
                                `Cluster ${
                                    Number.isFinite(
                                        numericCluster
                                    )
                                        ? numericCluster
                                        : 0
                                }`,

                            name:
                                `Cluster ${
                                    Number.isFinite(
                                        numericCluster
                                    )
                                        ? numericCluster
                                        : 0
                                }`,

                            customers:
                                Number.isFinite(
                                    customerCount
                                )
                                    ? customerCount
                                    : 0,

                            value:
                                Number.isFinite(
                                    customerCount
                                )
                                    ? customerCount
                                    : 0,

                            average_age:
                                0,

                            average_income:
                                0,

                            average_spending_score:
                                0,

                        };

                    }
                );

        }


        /*
         * Case 4:
         *
         * clusters object:
         *
         * {
         *     "0": 20,
         *     "1": 54
         * }
         */

        else if (
            backend?.clusters &&
            typeof backend.clusters === "object" &&
            !Array.isArray(
                backend.clusters
            )
        ) {

            normalizedSegments =
                Object.entries(
                    backend.clusters
                ).map(
                    ([cluster, count]) => {

                        const numericCluster =
                            Number(
                                String(
                                    cluster
                                ).match(
                                    /\d+/
                                )?.[0]
                            );


                        const customerCount =
                            Number(
                                count
                            );


                        return {

                            cluster:
                                Number.isFinite(
                                    numericCluster
                                )
                                    ? numericCluster
                                    : 0,

                            segment:
                                `Cluster ${
                                    Number.isFinite(
                                        numericCluster
                                    )
                                        ? numericCluster
                                        : 0
                                }`,

                            name:
                                `Cluster ${
                                    Number.isFinite(
                                        numericCluster
                                    )
                                        ? numericCluster
                                        : 0
                                }`,

                            customers:
                                Number.isFinite(
                                    customerCount
                                )
                                    ? customerCount
                                    : 0,

                            value:
                                Number.isFinite(
                                    customerCount
                                )
                                    ? customerCount
                                    : 0,

                            average_age:
                                0,

                            average_income:
                                0,

                            average_spending_score:
                                0,

                        };

                    }
                );

        }


        // =================================================
        // CLEAN SEGMENT VALUES
        // =================================================

        normalizedSegments =
            normalizedSegments.filter(
                item =>
                    item &&
                    Number.isFinite(
                        Number(
                            item.cluster
                        )
                    )
            );


        normalizedSegments.sort(
            (a, b) =>
                Number(a.cluster) -
                Number(b.cluster)
        );


        // =================================================
        // CUSTOMER COUNT FALLBACK
        // =================================================

        if (
            customers === 0 &&
            normalizedSegments.length > 0
        ) {

            customers =
                normalizedSegments.reduce(
                    (
                        total,
                        item
                    ) =>
                        total +
                        (
                            Number(
                                item.customers
                            ) || 0
                        ),
                    0
                );

        }


        // =================================================
        // RAW CUSTOMER DATA
        // =================================================

        const data =
            Array.isArray(
                backend?.data
            )
                ? backend.data
                : [];


        // =================================================
        // CUSTOMER SEGMENTS FOR PIE CHART
        // =================================================

        const customerSegments =
            normalizedSegments.map(
                item => ({

                    cluster:
                        item.cluster,

                    segment:
                        item.segment,

                    name:
                        item.name,

                    customers:
                        item.customers,

                    value:
                        item.value,

                    average_age:
                        item.average_age,

                    average_income:
                        item.average_income,

                    average_spending_score:
                        item.average_spending_score,

                })
            );


        // =================================================
        // LARGEST SEGMENT
        // =================================================

        let largestSegment =
            backend?.largest_segment
            ??
            null;


        if (
            !largestSegment &&
            normalizedSegments.length > 0
        ) {

            largestSegment =
                normalizedSegments.reduce(
                    (max, item) =>
                        item.customers >
                        max.customers
                            ? item
                            : max,
                    normalizedSegments[0]
                );

        }


        // =================================================
        // HIGHEST SPENDING SEGMENT
        // =================================================

        let highestSpendingSegment =
            backend?.highest_spending_segment
            ??
            null;


        if (
            !highestSpendingSegment &&
            normalizedSegments.length > 0
        ) {

            highestSpendingSegment =
                normalizedSegments.reduce(
                    (max, item) =>
                        item.average_spending_score >
                        max.average_spending_score
                            ? item
                            : max,
                    normalizedSegments[0]
                );

        }


        // =================================================
        // FINAL NORMALIZED RESULT
        // =================================================

        const result = {

            status:
                backend?.status
                ??
                payload?.status
                ??
                "success",

            available:
                backend?.available
                ??
                true,

            customers,

            segments:
                normalizedSegments,

            customer_segments:
                customerSegments,

            clusters:
                backend?.clusters
                ??
                Object.fromEntries(
                    normalizedSegments.map(
                        item => [

                            String(
                                item.cluster
                            ),

                            item.customers

                        ]
                    )
                ),

            segment_count:
                normalizedSegments.length,

            largest_segment:
                largestSegment,

            highest_spending_segment:
                highestSpendingSegment,

            data,

        };


        console.log(
            "NORMALIZED CUSTOMER RESPONSE:",
            result
        );


        return result;

    }

    catch (error) {

        console.error(
            "CUSTOMER SEGMENTATION API ERROR:",
            error
        );


        throw error;

    }

};


// =====================================================
// CUSTOMER STATISTICS
// =====================================================

export const fetchCustomerStats = async () => {

    try {

        const response =
            await api.get(
                "/customer/stats"
            );


        const payload =
            response?.data
            ??
            {};


        return (
            payload?.statistics
            ??
            payload?.data
            ??
            payload
            ??
            {}
        );

    }

    catch (error) {

        console.error(
            "CUSTOMER STATS API ERROR:",
            error
        );


        throw error;

    }

};


// =====================================================
// CUSTOMER HOME
// =====================================================

export const getCustomers = async () => {

    try {

        const response =
            await api.get(
                "/customer/"
            );


        return (
            response?.data
            ??
            {}
        );

    }

    catch (error) {

        console.error(
            "CUSTOMER HOME API ERROR:",
            error
        );


        throw error;

    }

};

