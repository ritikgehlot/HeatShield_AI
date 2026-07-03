import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { SimulationRequest } from "@/types/api";

export function useCities() {
  return useQuery({ queryKey: ["cities"], queryFn: api.cities });
}

export function useDashboard(cityId: number | undefined) {
  return useQuery({
    queryKey: ["dashboard", cityId],
    queryFn: () => api.dashboard(cityId as number),
    enabled: cityId !== undefined,
    refetchInterval: 5 * 60 * 1000,
  });
}

export function useWardDetail(wardId: number | undefined) {
  return useQuery({
    queryKey: ["ward", wardId],
    queryFn: () => api.wardDetail(wardId as number),
    enabled: wardId !== undefined,
  });
}

export function useWardTimeseries(wardId: number | undefined) {
  return useQuery({
    queryKey: ["ward-timeseries", wardId],
    queryFn: () => api.wardTimeseries(wardId as number),
    enabled: wardId !== undefined,
  });
}

export function useWardReport(wardId: number | undefined) {
  return useQuery({
    queryKey: ["ward-report", wardId],
    queryFn: () => api.wardReport(wardId as number),
    enabled: wardId !== undefined,
  });
}

export function useDataSourcesStatus() {
  return useQuery({ queryKey: ["data-sources"], queryFn: api.dataSourcesStatus, refetchInterval: 60 * 1000 });
}

export function useRefreshWeather() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (cityId?: number) => api.refreshWeather(cityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["data-sources"] });
    },
  });
}

export function useRefreshSatellite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (cityId?: number) => api.refreshSatellite(cityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["data-sources"] });
    },
  });
}

export function useCreateSimulation() {
  return useMutation({ mutationFn: (payload: SimulationRequest) => api.createSimulation(payload) });
}

export function useUploadWardFeaturesCsv() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => api.uploadWardFeaturesCsv(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["cities"] });
    },
  });
}

export function useUploadWardBoundaries() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => api.uploadWardBoundariesGeoJson(file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
  });
}
