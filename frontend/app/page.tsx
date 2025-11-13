import VoiceInterface from '@/components/VoiceInterface';
import { checkHealth } from '@/lib/api';

export const dynamic = 'force-static';

async function getServerData() {
  try {
    const health = await checkHealth();
    return {
      isHealthy: health.status === 'healthy',
      hospitalsIndexed: health.hospitals_indexed || 0,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    console.warn('Backend not available during build:', error);
    return {
      isHealthy: false,
      hospitalsIndexed: 0,
      timestamp: new Date().toISOString(),
    };
  }
}

export default async function Home() {
  const serverData = await getServerData();

  return (
    <main className="relative">
      <div className="absolute top-4 right-4 z-10">
        <div className={`
          px-4 py-2 rounded-full text-sm font-medium shadow-lg
          ${serverData.isHealthy 
            ? 'bg-green-100 text-green-800 border border-green-300' 
            : 'bg-yellow-100 text-yellow-800 border border-yellow-300'
          }
        `}>
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
            serverData.isHealthy ? 'bg-green-500' : 'bg-yellow-500'
          }`}></span>
          {serverData.isHealthy 
            ? `${serverData.hospitalsIndexed} hospitals indexed` 
            : 'Backend starting...'
          }
        </div>
      </div>
      <VoiceInterface />
    </main>
  );
}