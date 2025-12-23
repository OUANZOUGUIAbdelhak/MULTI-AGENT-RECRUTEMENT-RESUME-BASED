import { FileText, User, Code, Users, Award } from 'lucide-react';
import { Agent } from '../types';
import AgentCard from './AgentCard';

interface AgentProgressSectionProps {
  agents: Agent[];
}

const iconMap = {
  'rh-agent': FileText,
  'profile-agent': User,
  'technical-agent': Code,
  'softskills-agent': Users,
  'decision-agent': Award,
};

export default function AgentProgressSection({ agents }: AgentProgressSectionProps) {
  return (
    <section className="mb-12">
      <h2 className="text-2xl font-bold mb-6 text-white">Agent Progress</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {agents.map((agent, index) => {
          const Icon = iconMap[agent.id as keyof typeof iconMap];
          return (
            <AgentCard
              key={agent.id}
              agent={agent}
              index={index}
              icon={Icon}
            />
          );
        })}
      </div>
    </section>
  );
}

