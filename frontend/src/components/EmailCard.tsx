import { useState } from 'react';
import {
  Mail,
  User,
  Clock,
  CheckCircle2,
  XCircle,
  Send,
  Loader2,
  MessageSquare,
  AlertCircle,
  Trash2,
} from 'lucide-react';
import { clsx } from 'clsx';
import type { ReceivedEmail, EmailSuggestion } from '../types';
import { approveSuggestion, rejectSuggestion, deleteEmail } from '../services/api';
import { useToast } from '../hooks/useToast';

interface EmailCardProps {
  email: ReceivedEmail;
  suggestion?: EmailSuggestion;
  onUpdate: () => void;
}

export const EmailCard = ({ email, suggestion, onUpdate }: EmailCardProps) => {
  const [isApproving, setIsApproving] = useState(false);
  const [isRejecting, setIsRejecting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const { showToast, ToastComponent } = useToast();

  const handleApprove = async () => {
    if (!suggestion) return;

    setIsApproving(true);
    try {
      const response = await approveSuggestion(suggestion.id, true);
      if (response.success) {
        showToast('Email aprovado e enviado com sucesso!', 'success');
        onUpdate();
      } else {
        showToast('Erro ao aprovar email', 'error');
      }
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Erro ao aprovar email',
        'error'
      );
    } finally {
      setIsApproving(false);
    }
  };

  const handleReject = async () => {
    if (!suggestion) return;

    setIsRejecting(true);
    try {
      const response = await rejectSuggestion(suggestion.id);
      if (response.success) {
        showToast('Sugestão rejeitada', 'success');
        onUpdate();
      } else {
        showToast('Erro ao rejeitar sugestão', 'error');
      }
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Erro ao rejeitar sugestão',
        'error'
      );
    } finally {
      setIsRejecting(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Tem certeza que deseja deletar este email? Esta ação não pode ser desfeita.')) {
      return;
    }

    setIsDeleting(true);
    try {
      const response = await deleteEmail(email.id);
      if (response.success) {
        showToast('Email deletado com sucesso', 'success');
        onUpdate();
      } else {
        showToast('Erro ao deletar email', 'error');
      }
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Erro ao deletar email',
        'error'
      );
    } finally {
      setIsDeleting(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const getStatusBadge = (status?: string) => {
    if (!status) return null;

    const statusConfig = {
      pending: {
        label: 'Pendente',
        className: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        icon: Clock,
      },
      approved: {
        label: 'Aprovado',
        className: 'bg-blue-100 text-blue-800 border-blue-300',
        icon: CheckCircle2,
      },
      sent: {
        label: 'Enviado',
        className: 'bg-green-100 text-green-800 border-green-300',
        icon: Send,
      },
      rejected: {
        label: 'Rejeitado',
        className: 'bg-red-100 text-red-800 border-red-300',
        icon: XCircle,
      },
    };

    const config = statusConfig[status as keyof typeof statusConfig];
    if (!config) return null;

    const Icon = config.icon;

    return (
      <span
        className={clsx(
          'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium border',
          config.className
        )}
      >
        <Icon className="h-3 w-3" />
        {config.label}
      </span>
    );
  };

  const categoryBadge = email.category ? (
    <span
      className={clsx(
        'inline-flex items-center px-2 py-1 rounded text-xs font-medium',
        email.category === 'productive'
          ? 'bg-green-100 text-green-800'
          : 'bg-blue-100 text-blue-800'
      )}
    >
      {email.category === 'productive' ? 'Produtivo' : 'Não Produtivo'}
    </span>
  ) : null;

  return (
    <>
      <div className="bg-white rounded-lg border-2 border-gray-200 shadow-sm hover:shadow-md transition-shadow">
        {/* Email Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <Mail className="h-5 w-5 text-gray-500" />
                <h3 className="text-lg font-semibold text-gray-900">
                  {email.subject || '(Sem assunto)'}
                </h3>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <User className="h-4 w-4" />
                  <span className="font-medium">De:</span>
                  <span>{email.sender}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>{formatDate(email.received_at)}</span>
                </div>
              </div>
            </div>
            <div className="flex flex-col items-end gap-2">
              <div className="flex items-center gap-2">
                {categoryBadge}
                {suggestion && getStatusBadge(suggestion.status)}
              </div>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className={clsx(
                  'flex items-center gap-1 px-3 py-1.5 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg transition-colors',
                  isDeleting
                    ? 'opacity-50 cursor-not-allowed'
                    : 'hover:bg-red-100 hover:border-red-300'
                )}
                title="Deletar email"
              >
                {isDeleting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4" />
                )}
                <span>Deletar</span>
              </button>
            </div>
          </div>

          {/* Email Content */}
          <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200 max-h-48 overflow-y-auto">
            <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
              {email.content || '(Email sem conteúdo)'}
            </p>
          </div>

          {/* Confidence Score */}
          {email.confidence !== null && email.confidence !== undefined && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                <span>Confiança da classificação</span>
                <span className="font-medium">
                  {Math.round(email.confidence * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all"
                  style={{ width: `${email.confidence * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Suggestion Section */}
        {suggestion ? (
          <div className="p-6 bg-gradient-to-br from-primary-50 to-primary-100 border-t border-primary-200">
            <div className="flex items-center gap-2 mb-4">
              <MessageSquare className="h-5 w-5 text-primary-600" />
              <h4 className="font-semibold text-gray-900">Sugestão de Resposta</h4>
            </div>
            <div className="bg-white p-4 rounded-lg border border-primary-200 mb-4">
              <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                {suggestion.suggested_response}
              </p>
            </div>

            {/* Action Buttons */}
            {suggestion.status === 'pending' && (
              <div className="flex items-center gap-3">
                <button
                  onClick={handleApprove}
                  disabled={isApproving || isRejecting}
                  className={clsx(
                    'flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-lg font-medium transition-colors',
                    isApproving || isRejecting
                      ? 'opacity-50 cursor-not-allowed'
                      : 'hover:bg-green-700'
                  )}
                >
                  {isApproving ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Enviando...</span>
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4" />
                      <span>Aprovar e Enviar</span>
                    </>
                  )}
                </button>
                <button
                  onClick={handleReject}
                  disabled={isApproving || isRejecting}
                  className={clsx(
                    'flex items-center justify-center gap-2 px-4 py-3 bg-red-600 text-white rounded-lg font-medium transition-colors',
                    isApproving || isRejecting
                      ? 'opacity-50 cursor-not-allowed'
                      : 'hover:bg-red-700'
                  )}
                >
                  {isRejecting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <XCircle className="h-4 w-4" />
                  )}
                </button>
              </div>
            )}

            {suggestion.status === 'sent' && (
              <div className="flex items-center gap-2 text-green-700 bg-green-50 px-4 py-2 rounded-lg border border-green-200">
                <CheckCircle2 className="h-4 w-4" />
                <span className="text-sm font-medium">
                  Email enviado em {formatDate(suggestion.sent_at || '')}
                </span>
              </div>
            )}

            {suggestion.status === 'rejected' && (
              <div className="flex items-center gap-2 text-red-700 bg-red-50 px-4 py-2 rounded-lg border border-red-200">
                <AlertCircle className="h-4 w-4" />
                <span className="text-sm font-medium">Sugestão rejeitada</span>
              </div>
            )}
          </div>
        ) : (
          <div className="p-6 bg-gray-50 border-t border-gray-200">
            <div className="flex items-center gap-2 text-gray-500">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">Nenhuma sugestão gerada para este email</span>
            </div>
          </div>
        )}
      </div>
      {ToastComponent}
    </>
  );
};

