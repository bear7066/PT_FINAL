"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import {
    Drawer,
    DrawerClose,
    DrawerContent,
    DrawerDescription,
    DrawerFooter,
    DrawerHeader,
    DrawerTitle,
    DrawerTrigger,
} from "@/components/ui/drawer"

type DrawerProps = {
    cityName: string
}

export default function CityDrawer({ cityName }: DrawerProps) {
    const [cityData, setCityData] = React.useState<{ city_name: string; population: number } | null>(null)
    const [loading, setLoading] = React.useState(false)

    const fetchCityData = async () => {
        setLoading(true)
        try {
            const response = await fetch(`http://localhost:8080/api/search/city/${cityName}`, {
                credentials: "include",
            })
            const data = await response.json()
            setCityData(data)
        } catch (err) {
            console.error("Failed to fetch city data:", err)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex justify-center items-center min-h-screen">
            <Drawer>
                <DrawerTrigger asChild>
                    <Button variant="outline" onClick={fetchCityData}>
                        {cityName}
                    </Button>
                </DrawerTrigger>
                <DrawerContent>
                    <div className="mx-auto w-full max-w-sm">
                        <DrawerHeader>
                            <DrawerTitle>City Information</DrawerTitle>
                            <DrawerDescription>Details from city API</DrawerDescription>
                        </DrawerHeader>
                        <div className="p-4">
                            {loading ? (
                                <p className="text-center text-sm text-muted-foreground">Loading...</p>
                            ) : cityData ? (
                                <div className="space-y-2 text-sm">
                                    <p>
                                        <span className="font-semibold">City Name:</span> {cityData.city_name}
                                    </p>
                                    <p>
                                        <span className="font-semibold">Population:</span>{" "}
                                        {cityData.population.toLocaleString()}
                                    </p>
                                </div>
                            ) : (
                                <p className="text-center text-sm text-muted-foreground">No data loaded.</p>
                            )}
                        </div>
                        <DrawerFooter>
                            <DrawerClose asChild>
                                <Button variant="outline">Close</Button>
                            </DrawerClose>
                        </DrawerFooter>
                    </div>
                </DrawerContent>
            </Drawer>
        </div>
    )
}
