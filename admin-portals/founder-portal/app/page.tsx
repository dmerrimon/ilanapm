import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-white">
      <main className="flex flex-col items-center gap-8 max-w-2xl">
        <Image
          src="/logo.png"
          alt="Seleen Logo"
          width={300}
          height={80}
          priority
        />

        <h1 className="text-4xl md:text-5xl text-center text-black">
          Founder Portal
        </h1>

        <p className="text-center text-lg text-black">
          System administration and customer management for Seleen platform
        </p>

        <div className="flex gap-4 flex-col sm:flex-row">
          <Link
            href="/login"
            className="px-8 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors text-center"
          >
            Sign In
          </Link>
          <Link
            href="/dashboard"
            className="px-8 py-3 border border-black rounded-lg hover:bg-gray-50 transition-colors text-center text-black"
          >
            Go to Dashboard
          </Link>
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
          <div className="p-6 border border-gray-200 rounded-lg">
            <h3 className="text-xl mb-2 text-black">System Overview</h3>
            <p className="text-sm text-black opacity-70">
              Monitor all customers, revenue, and platform health metrics
            </p>
          </div>

          <div className="p-6 border border-gray-200 rounded-lg">
            <h3 className="text-xl mb-2 text-black">Customer Management</h3>
            <p className="text-sm text-black opacity-70">
              View and manage all customer organizations and licenses
            </p>
          </div>

          <div className="p-6 border border-gray-200 rounded-lg">
            <h3 className="text-xl mb-2 text-black">System Analytics</h3>
            <p className="text-sm text-black opacity-70">
              Track platform usage, ML performance, and system logs
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
