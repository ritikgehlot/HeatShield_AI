import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useCities } from "@/hooks/useApi";

interface CityContextValue {
  cityId: number | undefined;
  setCityId: (id: number) => void;
}

const CityContext = createContext<CityContextValue>({ cityId: undefined, setCityId: () => {} });

export function CityProvider({ children }: { children: ReactNode }) {
  const { data: cities } = useCities();
  const [cityId, setCityId] = useState<number | undefined>(undefined);

  useEffect(() => {
    if (cities && cities.length > 0 && cityId === undefined) {
      setCityId(cities[0].id);
    }
  }, [cities, cityId]);

  return <CityContext.Provider value={{ cityId, setCityId }}>{children}</CityContext.Provider>;
}

export function useSelectedCity() {
  return useContext(CityContext);
}
