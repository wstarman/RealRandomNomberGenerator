import { COLORS } from '../constants/colors';
import { fireEvent, render, screen, waitFor } from '../test-utils';
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
      expect(screen.getByText(/source: microphone/i)).toBeInTheDocument();
    });
  });

  it('shows error alert on failed API call', async () => {
    const alertMock = jest.spyOn(window, 'alert').mockImplementation();
    const consoleMock = jest.spyOn(console, 'error').mockImplementation();

    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    render(<RandomNumberDisplay />);

    const button = screen.getByRole('button', { name: /pick a number/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalled();
    });

    alertMock.mockRestore();
    consoleMock.mockRestore();
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
    const consoleMock = jest.spyOn(console, 'error').mockImplementation();

    // Mock fetch to never resolve (simulates hanging request)
    (global.fetch as jest.Mock).mockImplementation(
      () =>
        new Promise((_resolve, reject) => {
          // Simulate AbortController behavior with fake timers
          setTimeout(() => {
            const error = new Error('AbortError');
            error.name = 'AbortError';
            reject(error);
          }, 5000);
        })
    );

    render(<RandomNumberDisplay />);

    const button = screen.getByRole('button', { name: /pick a number/i });
    fireEvent.click(button);

    // Fast-forward time
    jest.advanceTimersByTime(5000);

    await waitFor(
      () => {
        expect(alertMock).toHaveBeenCalledWith(expect.stringContaining('timed out'));
      },
      { timeout: 100 }
    );

    jest.useRealTimers();
    alertMock.mockRestore();
    consoleMock.mockRestore();
  });

  it('validates API response structure', async () => {
    const alertMock = jest.spyOn(window, 'alert').mockImplementation();
    const consoleMock = jest.spyOn(console, 'error').mockImplementation();

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
    consoleMock.mockRestore();
  });

  it('shows green status indicator when source is microphone', async () => {
    const mockData = {
      rand: 0.5,
      source: 'microphone',
      timestamp: '2025-12-11T10:30:00.123456',
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    render(<RandomNumberDisplay />);
    fireEvent.click(screen.getByRole('button', { name: /pick a number/i }));

    await waitFor(() => {
      const dot = screen.getByTestId('status-indicator-dot');
      expect(dot).toHaveStyle({ backgroundColor: COLORS.STATUS_MICROPHONE });
    });
  });

  it('shows red status indicator when source is fallback', async () => {
    const mockData = {
      rand: 0.5,
      source: 'fallback',
      timestamp: '2025-12-11T10:30:00.123456',
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    render(<RandomNumberDisplay />);
    fireEvent.click(screen.getByRole('button', { name: /pick a number/i }));

    await waitFor(() => {
      const dot = screen.getByTestId('status-indicator-dot');
      expect(dot).toHaveStyle({ backgroundColor: COLORS.STATUS_FALLBACK });
    });
  });

  it('displays fallback source metadata when source is fallback', async () => {
    const mockData = {
      rand: 0.987654321,
      source: 'fallback',
      timestamp: '2025-12-11T10:30:00.123456',
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    render(<RandomNumberDisplay />);
    fireEvent.click(screen.getByRole('button', { name: /pick a number/i }));

    await waitFor(() => {
      expect(screen.getByText(/0.987654321/)).toBeInTheDocument();
      expect(screen.getByText(/source: fallback/i)).toBeInTheDocument();
    });
  });

  it('shows loading overlay during API request', async () => {
    // Mock fetch to delay response
    (global.fetch as jest.Mock).mockImplementation(
      () =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                ok: true,
                json: async () => ({
                  rand: 0.5,
                  source: 'microphone',
                  timestamp: '2025-12-11T10:30:00',
                }),
              }),
            1000
          )
        )
    );

    render(<RandomNumberDisplay />);
    fireEvent.click(screen.getByRole('button', { name: /pick a number/i }));

    // Mantine LoadingOverlay renders a loader element with role="presentation" containing an SVG
    // When visible=true, a loader SVG is rendered in the DOM
    await waitFor(() => {
      const loader = document.querySelector(
        '.mantine-Loader-root, [class*="mantine-LoadingOverlay"]'
      );
      expect(loader).toBeInTheDocument();
    });
  });
});
