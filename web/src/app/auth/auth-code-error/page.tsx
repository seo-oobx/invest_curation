import { Button } from "@/components/ui/button"
import Link from "next/link"
import { AlertCircle } from "lucide-react"

export default function AuthErrorPage({
    searchParams,
}: {
    searchParams: { error?: string }
}) {
    return (
        <div className="flex h-screen w-full flex-col items-center justify-center bg-slate-50 px-4">
            <div className="flex w-full max-w-md flex-col items-center space-y-6 rounded-lg border bg-white p-8 shadow-sm text-center">
                <div className="rounded-full bg-red-100 p-3">
                    <AlertCircle className="h-6 w-6 text-red-600" />
                </div>

                <div className="space-y-2">
                    <h1 className="text-2xl font-bold tracking-tight text-slate-900">
                        Authentication Error
                    </h1>
                    <p className="text-sm text-slate-500">
                        There was a problem signing you in.
                    </p>
                </div>

                {searchParams.error && (
                    <div className="w-full rounded-md bg-red-50 p-3 text-sm text-red-800 break-words">
                        Error: {searchParams.error}
                    </div>
                )}

                <div className="flex w-full flex-col space-y-2">
                    <Button asChild className="w-full">
                        <Link href="/">Return to Home</Link>
                    </Button>
                </div>
            </div>
        </div>
    )
}
