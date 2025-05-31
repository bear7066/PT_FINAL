"use client";
import React from "react";
import { PinContainer } from "../ui/3d-pin";

export function AnimatedPinDemo() {
    return (
        <div className="h-auto w-full flex flex-col md:flex-row items-center justify-center gap-8">
            <PinContainer
                title="Taipei"
                href="/city/Taipei"
            >
                <div className="flex basis-full flex-col p-4 tracking-tight text-slate-100/50 w-[20rem] h-[20rem]">
                    <h3 className="max-w-xs !pb-2 !m-0 font-bold text-base text-slate-100">
                        Taipei
                    </h3>
                    <div className="text-base !m-0 !p-0 font-normal">
                        <span className="text-slate-500">
                            Taipei, the vibrant capital of Taiwan, is a city that blends modern innovation with rich cultural heritage.
                        </span>
                    </div>
                    <div className="flex flex-1 w-full rounded-lg mt-4 bg-gradient-to-br from-violet-500 via-purple-500 to-blue-500" />
                </div>
            </PinContainer>

            <PinContainer
                title="Phoenix"
                href="/city/Phoenix"
            >
                <div className="flex basis-full flex-col p-4 tracking-tight text-slate-100/50 w-[20rem] h-[20rem]">
                    <h3 className="max-w-xs !pb-2 !m-0 font-bold text-base text-slate-100">
                        Phoenix
                    </h3>
                    <div className="text-base !m-0 !p-0 font-normal">
                        <span className="text-slate-500">
                            Phoenix, the capital of Arizona, is known for its year-round sunshine and desert landscapes.
                        </span>
                    </div>
                    <div className="flex flex-1 w-full rounded-lg mt-4 bg-gradient-to-br from-pink-500 via-red-500 to-yellow-500" />
                </div>
            </PinContainer>
        </div >
    );
}
