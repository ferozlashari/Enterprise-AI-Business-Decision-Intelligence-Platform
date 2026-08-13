
export default function CustomerTable({ customers = [] }) {

    return (

        <div className="
            bg-slate-900
            border
            border-slate-800
            rounded-xl
            p-5
        ">

            <h2 className="
                text-white
                font-bold
                text-xl
                mb-4
            ">

                Customer Segment Analysis

            </h2>


            {customers.length === 0 ? (

                <p className="
                    text-slate-500
                    text-sm
                    text-center
                    py-10
                ">

                    No customer segmentation data available.

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

                            {customers.map(
                                (row, index) => (

                                    <tr
                                        key={
                                            row.cluster ??
                                            index
                                        }
                                        className="
                                            border-b
                                            border-slate-800/60
                                        "
                                    >

                                        <td className="
                                            py-3
                                            pr-4
                                            text-slate-200
                                            font-medium
                                        ">

                                            Cluster{" "}

                                            {row.cluster ??
                                                index}

                                        </td>


                                        <td className="
                                            py-3
                                            pr-4
                                            text-slate-300
                                        ">

                                            {Number(
                                                row.customers ??
                                                0
                                            ).toLocaleString()}

                                        </td>


                                        <td className="
                                            py-3
                                            pr-4
                                            text-slate-300
                                        ">

                                            {Number(
                                                row.average_age ??
                                                0
                                            ).toFixed(2)}

                                        </td>


                                        <td className="
                                            py-3
                                            pr-4
                                            text-slate-300
                                        ">

                                            {Number(
                                                row.average_income ??
                                                0
                                            ).toFixed(2)}

                                        </td>


                                        <td className="
                                            py-3
                                            text-slate-300
                                        ">

                                            {Number(
                                                row.average_spending_score ??
                                                0
                                            ).toFixed(2)}

                                        </td>

                                    </tr>

                                )
                            )}

                        </tbody>

                    </table>

                </div>

            )}

        </div>

    );

}

