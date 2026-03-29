import { useMutation } from "@tanstack/react-query";

import { predict } from "../utils/api";

export function usePredict() {
  return useMutation({ mutationFn: predict });
}
