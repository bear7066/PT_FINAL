"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AnimatedPinDemo } from "@/components/cell/AnimatedPinDemo";


export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const checkLogin = async () => {
      try {
        const res = await fetch("http://localhost:8080/api/user/check", {
          credentials: "include",
        });

        if (!res.ok) {
          router.push("/login");
        }
        // 可選：你可以儲存使用者資訊以供畫面使用
        // const user = await res.json();
      } catch (err) {
        console.error("Error checking login", err);
        router.push("/login");
      }
    };

    checkLogin();
  }, [router]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <AnimatedPinDemo />
    </main>
  );
}
