import { render, screen, fireEvent, waitFor } from '../test-utils';
import RandomNumberDisplay from './RandomNumberDisplay';

// Mock fetch
global.fetch = jest.fn();

describe('RandomNumberDisplay', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the component with initial state', () => {
    render(<RandomNumberDisplay />);

    expect(screen.getByRole('heading', { name: /random number generator/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /pick a number/i })).toBeInTheDocument();
  });

  it('displays random number after successful API call', async () => {
    const mockData = {
      rand: 0.123456789,
      source: 'microphone',
      timestamp: '2025-12-11T10:30:00.123456',
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    render(<RandomNumberDisplay />);

    const button = screen.getByRole('button', { name: /pick a number/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/0.123456789/)).toBeInTheDocument();
      expect(screen.getByText(/microphone/i)).toBeInTheDocument();
    });
  });

  it('shows error alert on failed API call', async () => {
    const alertMock = jest.spyOn(window, 'alert').mockImplementation();

    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    render(<RandomNumberDisplay />);

    const button = screen.getByRole('button', { name: /pick a number/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalled();
    });

    alertMock.mockRestore();
  });

  it('disables button during loading', async () => {
    (global.fetch as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    );

    render(<RandomNumberDisplay />);

    const button = screen.getByRole('button', { name: /pick a number/i });
    fireEvent.click(button);

    expect(button).toBeDisabled();
  });

  it('shows timeout error after 5 seconds', async () => {
    jest.useFakeTimers();
    const alertMock = jest.spyOn(window, 'alert').mockImplementation();

    (global.fetch as jest.Mock).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<RandomNumberDisplay />);

    const button = screen.getByRole('button', { name: /pick a number/i });
    fireEvent.click(button);

    jest.advanceTimersByTime(5000);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(expect.stringContaining('timed out'));
    });

    jest.useRealTimers();
    alertMock.mockRestore();
  });

  it('validates API response structure', async () => {
    const alertMock = jest.spyOn(window, 'alert').mockImplementation();

    // Invalid response (missing fields)
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ invalid: 'data' }),
    });

    render(<RandomNumberDisplay />);

    const button = screen.getByRole('button', { name: /pick a number/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith(expect.stringContaining('invalid data'));
    });

    alertMock.mockRestore();
  });
});
