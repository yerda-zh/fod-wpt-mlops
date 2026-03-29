import { useQuery } from "@tanstack/react-query";

import { getHistory } from "../utils/api";

export function useHistory() {
  return useQuery({
    queryKey: ["predictions"],
    queryFn: getHistory,
    refetchInterval: 30000,
  });
}
