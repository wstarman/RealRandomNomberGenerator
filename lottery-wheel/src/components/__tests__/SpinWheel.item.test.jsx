import { render, screen, fireEvent, within } from "@testing-library/react";
import SpinWheel from ".././SpinWheel";

describe("TC-UIW-001: Item Management", () => {
  test("add items updates wheel segments", () => {
    render(<SpinWheel />);

    const textarea = screen.getByPlaceholderText(/Enter options/i);
    const wheel = screen.getByTestId("wheel");

    fireEvent.change(textarea, {
      target: { value: "Item 1\nItem 2" }
    });

    // There should be 2 segment labels in the wheel.
    expect(within(wheel).getByText("Item 1")).toBeInTheDocument();
    expect(within(wheel).getByText("Item 2")).toBeInTheDocument();
  });

  test("delete item updates wheel immediately", () => {
    render(<SpinWheel />);

    const textarea = screen.getByPlaceholderText(/Enter options/i);
    const wheel = screen.getByTestId("wheel");

    fireEvent.change(textarea, {
      target: { value: "Item 1\nItem 2" }
    });

    // delete Item 1
    fireEvent.change(textarea, {
      target: { value: "Item 2" }
    });

    expect(within(wheel).queryByText("Item 1")).toBeNull();
    expect(within(wheel).getByText("Item 2")).toBeInTheDocument();
  });

  test("edit item updates wheel label", () => {
    render(<SpinWheel />);

    const textarea = screen.getByPlaceholderText(/Enter options/i);
    const wheel = screen.getByTestId("wheel");

    fireEvent.change(textarea, {
      target: { value: "Item 2" }
    });

    fireEvent.change(textarea, {
      target: { value: "Edited Item" }
    });

    expect(within(wheel).getByText("Edited Item")).toBeInTheDocument();
  });
});
