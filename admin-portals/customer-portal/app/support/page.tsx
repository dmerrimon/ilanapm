'use client';

import Image from "next/image";
import Link from "next/link";

export default function SupportPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-lg">
        <div className="flex flex-col items-center">
          <Image
            src="/logo.png"
            alt="Seleen Logo"
            width={200}
            height={53}
            priority
          />
          <h2 className="mt-6 text-center text-3xl">
            Need Help?
          </h2>
          <p className="mt-2 text-center text-sm opacity-70">
            Contact your organization administrator for support
          </p>
        </div>

        <div className="mt-8 space-y-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-blue-900 mb-3">
              Don't have an account?
            </h3>
            <p className="text-blue-800 mb-4">
              Only organization administrators can create new accounts. Please contact your organization's Seleen administrator to request access.
            </p>
            <p className="text-sm text-blue-700">
              Your administrator can add you from the Users section in the customer portal.
            </p>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-3">
              Need additional assistance?
            </h3>
            <p className="text-gray-700 mb-4">
              For technical support or general inquiries, please reach out to our support team:
            </p>
            <a
              href="mailto:support@seleen.io"
              className="inline-block px-6 py-3 bg-black text-white rounded-md hover:bg-gray-800 transition-colors"
            >
              Email Support
            </a>
          </div>
        </div>

        <div className="text-center pt-4">
          <Link href="/login" className="text-sm hover:underline">
            Back to sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
