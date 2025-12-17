export function mockFetchSuccess(rand = 0.45, source = "microphone") {
  jest.spyOn(global, "fetch").mockResolvedValue({
    ok: true,
    json: async () => ({
      rand,
      source,
    }),
  });
}

export function mockFetchFail() {
  jest.spyOn(global, "fetch").mockRejectedValue(
    new Error("API not available")
  );
}
