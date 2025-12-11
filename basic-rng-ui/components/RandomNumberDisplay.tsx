import { useState } from 'react';
import { Container, Title, Text, Button, LoadingOverlay } from '@mantine/core';
import { COLORS } from '../constants/colors';

interface RandomData {
  rand: number | null;
  source: string;
  timestamp: string;
}

export default function RandomNumberDisplay() {
  const [data, setData] = useState<RandomData>({
    rand: null,
    source: 'fallback',
    timestamp: '',
  });
  const [loading, setLoading] = useState(false);

  const handlePickNumber = async () => {
    setLoading(true);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${apiUrl}/api/random`, {
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      // Validate HTTP response
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const apiData = await response.json();

      // Validate response structure
      if (typeof apiData.rand !== 'number' || !apiData.source || !apiData.timestamp) {
        throw new Error('Invalid API response format');
      }

      setData({
        rand: apiData.rand, // CRITICAL: use .rand NOT .value (avoid lottery-wheel bug)
        source: apiData.source,
        timestamp: apiData.timestamp,
      });
    } catch (error) {
      console.error('Failed to fetch random number:', error);

      let errorMessage = 'Failed to generate random number. Please try again.';

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = 'Request timed out. Please check your connection and try again.';
        } else if (error.message.includes('API error: 500')) {
          errorMessage = 'Backend server error. Please ensure the backend is running.';
        } else if (error.message.includes('Invalid API response')) {
          errorMessage = 'Received invalid data from server. Please try again.';
        } else if (error.message.includes('Failed to fetch')) {
          errorMessage =
            'Cannot connect to backend. Please ensure the server is running at http://127.0.0.1:8000';
        }
      }

      alert(errorMessage);
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
    }
  };

  const statusColor = data.source === 'microphone'
    ? COLORS.STATUS_MICROPHONE
    : COLORS.STATUS_FALLBACK;

  return (
    <Container size="xs" style={{ position: 'relative', paddingTop: 60 }}>
      <LoadingOverlay visible={loading} />

      {/* Status Indicator with Visual Text */}
      <div
        role="status"
        aria-label={`Random number source: ${data.source}`}
        style={{
          position: 'fixed',
          top: 20,
          right: 20,
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '6px 12px',
          backgroundColor: 'white',
          borderRadius: 16,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
      >
        <div
          style={{
            width: 12,
            height: 12,
            borderRadius: '50%',
            backgroundColor: statusColor,
          }}
        />
        <Text size="sm" fw={500}>
          {data.source === 'microphone' ? 'Microphone' : 'Fallback'}
        </Text>
      </div>

      <Title order={1} style={{ textAlign: 'center', marginBottom: 40 }}>
        Random Number Generator
      </Title>

      {data.rand !== null && (
        <>
          <Text size="52px" fw={700} style={{ textAlign: 'center', marginBottom: 20 }}>
            {data.rand.toFixed(9)}
          </Text>
          <Text size="md" style={{ textAlign: 'center' }}>
            Source: {data.source}
          </Text>
          <Text size="md" c="dimmed" style={{ textAlign: 'center', marginBottom: 40 }}>
            {data.timestamp}
          </Text>
        </>
      )}

      <Button fullWidth size="lg" onClick={handlePickNumber} disabled={loading}>
        Pick a Number
      </Button>
    </Container>
  );
}
