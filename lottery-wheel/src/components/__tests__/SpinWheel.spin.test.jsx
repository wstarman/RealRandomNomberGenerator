import { act, render, screen, fireEvent } from "@testing-library/react";
import SpinWheel from "../SpinWheel";
import { mockFetchSuccess, mockFetchFail } from "../../test/mocks/mockFetch";

describe("TC-UIW-002: Spin and Winner Selection", () => {

  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.clearAllTimers();
    jest.restoreAllMocks();
  });

  test("spin selects correct winner based on API rand", async () => {
    mockFetchSuccess(0.45, "microphone");

    render(<SpinWheel />);

    fireEvent.change(
      screen.getByPlaceholderText(/Enter options/i),
      { target: { value: "Item 1\nItem 2\nItem 3\nItem 4\nItem 5" } }
    );

    await act(async () => {
        fireEvent.click(screen.getByText("Start Lottery"));
    });

    // 尚未結束動畫
    expect(screen.queryByText(/Winner:/)).toBeNull();

    // 快轉 3 秒
    jest.advanceTimersByTime(3000);

    expect(
      await screen.findByText(/🎉\s*Winner:\s*Item 3/i)
    ).toBeInTheDocument();

    expect(screen.getByText(/RNG Mode: microphone/i)).toBeInTheDocument();
  });

  test("fallback to Math.random when API fails", async () => {
    mockFetchFail();

    render(<SpinWheel />);

    fireEvent.change(
      screen.getByPlaceholderText(/Enter options/i),
      { target: { value: "A\nB" } }
    );

    fireEvent.click(screen.getByText("Start Lottery"));

    jest.advanceTimersByTime(3000);

    expect(screen.getByText(/RNG Mode: aip unused/i)).toBeInTheDocument();
  });
});
