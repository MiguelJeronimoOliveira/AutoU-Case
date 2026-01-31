import { Settings as SettingsIcon, Bot, Shield, Database } from 'lucide-react';
import { AutoReplySettings } from '../components/AutoReplySettings';
import { StorageSettings } from '../components/StorageSettings';
import { useToast } from '../hooks/useToast';

export const Settings = () => {
  const { ToastComponent } = useToast();

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center gap-3">
          <SettingsIcon className="h-8 w-8 text-primary-600" />
          <h1 className="text-4xl font-bold text-gray-900">Configurações</h1>
        </div>
        <p className="text-gray-600">
          Gerencie as configurações avançadas do sistema
        </p>
      </div>

      <div className="space-y-6">
        {/* Auto-Reply Settings Section */}
        <section className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <div className="flex items-center gap-3 mb-6">
            <Bot className="h-6 w-6 text-primary-600" />
            <h2 className="text-2xl font-semibold text-gray-900">
              Resposta Automática
            </h2>
          </div>
          <p className="text-gray-600 mb-6">
            Configure como o sistema deve responder automaticamente aos emails recebidos.
          </p>
          <AutoReplySettings />
        </section>

        {/* Future Settings Sections */}
        <section className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 opacity-60">
          <div className="flex items-center gap-3 mb-6">
            <Shield className="h-6 w-6 text-gray-400" />
            <h2 className="text-2xl font-semibold text-gray-500">
              Segurança e Privacidade
            </h2>
          </div>
          <p className="text-gray-500">
            Configurações de segurança estarão disponíveis em breve.
          </p>
        </section>

        {/* Storage and Backup Section */}
        <section className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <div className="flex items-center gap-3 mb-6">
            <Database className="h-6 w-6 text-primary-600" />
            <h2 className="text-2xl font-semibold text-gray-900">
              Armazenamento e Backup
            </h2>
          </div>
          <StorageSettings />
        </section>
      </div>

      {ToastComponent}
    </div>
  );
};

