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
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${apiUrl}/api/random`);
      if (!response.ok) throw new Error('API request failed');
      const apiData = await response.json();
      setData({
        rand: apiData.rand, // CRITICAL: use .rand NOT .value (avoid lottery-wheel bug)
        source: apiData.source,
        timestamp: apiData.timestamp,
      });
    } catch (error) {
      console.error('Failed to fetch random number:', error);
      alert('Failed to generate random number. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const statusColor = data.source === 'microphone'
    ? COLORS.STATUS_MICROPHONE
    : COLORS.STATUS_FALLBACK;

  return (
    <Container size="xs" style={{ position: 'relative', paddingTop: 60 }}>
      <LoadingOverlay visible={loading} />

      {/* Status Indicator */}
      <div
        style={{
          position: 'fixed',
          top: 20,
          right: 20,
          width: 12,
          height: 12,
          borderRadius: '50%',
          backgroundColor: statusColor,
        }}
      />

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
