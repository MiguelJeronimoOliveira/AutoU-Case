import { EmailHistory } from '../components/EmailHistory';

export const History = () => {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Histórico de Emails
        </h1>
        <p className="text-gray-600">
          Visualize todos os emails analisados com suas categorias e sugestões
          de resposta
        </p>
      </div>

      <EmailHistory />
    </div>
  );
};

