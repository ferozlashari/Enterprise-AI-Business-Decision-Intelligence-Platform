import { Link } from "react-router-dom";

export default function NotFound() {
    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
            <div className="text-center">

                <div className="text-8xl font-bold text-blue-500 mb-4">
                    404
                </div>

                <h1 className="text-3xl font-bold text-white mb-3">
                    Page Not Found
                </h1>

                <p className="text-gray-400 mb-8">
                    The page you are looking for does not exist.
                </p>

                <div className="flex justify-center gap-4">

                    <Link
                        to="/"
                        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold"
                    >
                        Go to Dashboard
                    </Link>

                    <Link
                        to="/login"
                        className="bg-slate-800 hover:bg-slate-700 text-gray-200 px-6 py-3 rounded-lg font-semibold"
                    >
                        Login
                    </Link>

                </div>

            </div>
        </div>
    );
}