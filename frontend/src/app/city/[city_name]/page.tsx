import CityDrawer from "../drawer"

type PageProps = {
    params: {
        city_name: string
    }
}


export default function CityPage({ params }: PageProps) {

    const { city_name } = params

    return <CityDrawer cityName={city_name} />
}
