"""Script para gerar uma grande quantidade de dados de treinamento de emails produtivos e não produtivos."""

import json
import random
import re
from typing import List, Dict
from datetime import datetime

# Clientes e empresas
CLIENTES = [
    ("Jaguar Land Rover", "jaguarlandrover.com"),
    ("L'Oréal", "loreal.com"),
    ("Nestlé", "nestle.com"),
    ("Stellantis", "stellantis.com"),
    ("Vale", "vale.com"),
    ("Petrobras", "petrobras.com.br"),
    ("Ambev", "ambev.com.br"),
    ("Bradesco", "bradesco.com.br"),
    ("Itaú", "itau.com.br"),
    ("Unilever", "unilever.com"),
]

# Nomes de pessoas
NOMES = [
    "Miguel", "Ana", "Carlos", "Juliana", "Roberto", "Patricia", "Thiago", "Beatriz",
    "Eduardo", "Camila", "Ricardo", "Amanda", "Paulo", "Larissa", "Lucas", "Sofia",
    "Fernando", "Mariana", "Gabriel", "Isabella", "Rafael", "Renata", "Daniel", "Ana Paula",
    "Roberto", "Carolina", "Henrique", "Vanessa", "André", "Cristina", "Bruno", "Tatiana"
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira",
    "Lima", "Costa", "Rocha", "Martins", "Carvalho", "Almeida", "Lopes", "Fernandes",
    "Araújo", "Mendes", "Torres", "Gomes", "Ribeiro", "Barbosa", "Reis", "Monteiro"
]

CARGOS = [
    "Gerente de Projetos", "Diretor de Operações", "Coordenador de Manutenção",
    "Analista de Sistemas", "Gerente de TI", "Supervisor de Produção",
    "Diretor de Inovação", "Gerente de Qualidade", "Diretor de Transformação Digital",
    "Gerente de Planejamento", "Gerente de Supply Chain", "Gerente de Analytics",
    "Coordenador de Manutenção", "Analista de Sistemas", "Supervisor de Produção"
]

# Templates de emails PRODUTIVOS (label 1)
PRODUCTIVE_TEMPLATES = [
    # Solicitações de suporte técnico
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: Miguel Jeronimo <miguel.jeronimo@autou.com>
Assunto: {assunto}

{nome},

{saudacao}. Estamos enfrentando {problema} no sistema de {sistema} instalado na {localizacao}.

Detalhes do problema:
- {detalhe1}
- {detalhe2}
- {detalhe3}

Isso está impactando nossa operação e precisamos de suporte técnico {urgencia}. Por favor, entre em contato o mais rápido possível.

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}
Tel: {telefone}""",
        "variations": {
            "problema": [
                "um problema crítico", "falhas intermitentes", "erros de comunicação",
                "problemas de performance", "falhas no sistema", "erros de sincronização",
                "problemas de integração", "falhas de autenticação", "erros de processamento"
            ],
            "sistema": [
                "automação", "automação de produção", "sistema de IA", "sistema de qualidade",
                "plataforma de gestão", "sistema de rastreabilidade", "sistema de monitoramento"
            ],
            "localizacao": [
                "nossa fábrica", "nossa unidade de produção", "nossa linha de produção",
                "nosso centro de distribuição", "nossa planta", "nossa unidade"
            ],
            "detalhe1": [
                "Sistema apresentando latência acima do normal",
                "Erros registrados no log do sistema",
                "Falhas de comunicação entre módulos",
                "Timeout em operações críticas",
                "Alto uso de CPU e memória"
            ],
            "detalhe2": [
                "Produção impactada durante picos",
                "Operações críticas interrompidas",
                "Sincronização de dados falhando",
                "Interface do usuário não respondendo",
                "Relatórios não sendo gerados"
            ],
            "detalhe3": [
                "Precisamos de investigação urgente",
                "Situação requer atenção imediata",
                "Impacto direto na produtividade",
                "Risco de parada completa da operação",
                "Necessário suporte técnico especializado"
            ],
            "urgencia": [
                "urgente", "o quanto antes", "com prioridade", "imediatamente", "com urgência"
            ],
            "saudacao": [
                "Bom dia", "Boa tarde", "Olá", "Prezado Miguel"
            ],
            "assunto": [
                "URGENTE - Problema no Sistema de Automação",
                "Solicitação de Suporte Técnico - Sistema com Falhas",
                "Problema Crítico no Sistema",
                "Falhas no Sistema de Automação",
                "Solicitação de Suporte Urgente"
            ]
        }
    },
    
    # Solicitações de informações/orçamento
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: Miguel Jeronimo <miguel.jeronimo@autou.com>
Assunto: {assunto}

{nome},

{saudacao}. Estamos interessados em {projeto} e gostaria de solicitar algumas informações.

Precisamos saber:
1. {pergunta1}
2. {pergunta2}
3. {pergunta3}
4. {pergunta4}

{contexto}

Preciso dessas informações para {objetivo}. Seria possível agendarmos uma reunião {prazo} para discutirmos?

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "projeto": [
                "expandir o projeto de automação", "implementar um novo sistema de IA",
                "desenvolver uma solução customizada", "adicionar funcionalidades ao sistema atual",
                "realizar uma atualização do sistema", "implementar melhorias no sistema"
            ],
            "pergunta1": [
                "Qual o investimento necessário?",
                "Qual o prazo de implementação?",
                "Quais são os requisitos técnicos?",
                "Qual a viabilidade técnica?",
                "Quais funcionalidades estão incluídas?"
            ],
            "pergunta2": [
                "Qual o cronograma do projeto?",
                "Quais são as etapas de implementação?",
                "Qual o escopo detalhado?",
                "Quais são as dependências?",
                "Qual a metodologia de trabalho?"
            ],
            "pergunta3": [
                "Inclui treinamento da equipe?",
                "Qual o suporte pós-implementação?",
                "Quais são as garantias oferecidas?",
                "Há possibilidade de parcelamento?",
                "Qual a política de manutenção?"
            ],
            "pergunta4": [
                "Quando podemos iniciar?",
                "Quais são os próximos passos?",
                "Precisamos de algum recurso adicional?",
                "Há integração com sistemas existentes?",
                "Qual a capacidade de escalabilidade?"
            ],
            "contexto": [
                "Estamos planejando apresentar ao comitê executivo no final do mês.",
                "Precisamos incluir no orçamento do próximo trimestre.",
                "A diretoria solicitou uma análise detalhada.",
                "Estamos avaliando diferentes fornecedores.",
                "Precisamos tomar uma decisão estratégica."
            ],
            "objetivo": [
                "apresentar ao board", "incluir no orçamento", "tomar uma decisão",
                "planejar a implementação", "avaliar a viabilidade"
            ],
            "prazo": [
                "esta semana", "na próxima semana", "o quanto antes", "nos próximos dias"
            ],
            "saudacao": ["Bom dia", "Boa tarde", "Olá", "Prezado Miguel"],
            "assunto": [
                "Solicitação de Proposta - Projeto de Automação",
                "Dúvidas sobre Expansão do Projeto",
                "Solicitação de Informações Técnicas",
                "Proposta para Novo Projeto",
                "Reunião sobre Projeto de IA"
            ]
        }
    },
    
    # Solicitações de reunião
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: Miguel Jeronimo <miguel.jeronimo@autou.com>
Assunto: {assunto}

{nome},

{saudacao}. Gostaria de agendar uma reunião para discutirmos {topico}.

Tópicos a serem discutidos:
- {topico1}
- {topico2}
- {topico3}

{contexto}

Seria possível agendarmos para {prazo}? Por favor, me envie algumas opções de horários disponíveis.

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "topico": [
                "o andamento do projeto", "próximas etapas do projeto",
                "questões técnicas do sistema", "expansão do projeto",
                "melhorias no sistema atual", "novos requisitos"
            ],
            "topico1": [
                "Status atual das entregas",
                "Arquitetura da solução",
                "Cronograma de implementação",
                "Integração com sistemas existentes",
                "Métricas de sucesso"
            ],
            "topico2": [
                "Próximos marcos do projeto",
                "Requisitos técnicos",
                "Planejamento de recursos",
                "Gestão de riscos",
                "Treinamento da equipe"
            ],
            "topico3": [
                "Questões pendentes",
                "Dependências e bloqueios",
                "Orçamento e investimento",
                "Suporte e manutenção",
                "Escalabilidade da solução"
            ],
            "contexto": [
                "Precisamos alinhar antes da próxima fase.",
                "Temos algumas questões que precisam ser esclarecidas.",
                "A diretoria solicitou uma atualização.",
                "Estamos planejando os próximos passos.",
                "Há algumas decisões importantes a serem tomadas."
            ],
            "prazo": [
                "esta semana", "na próxima semana", "o quanto antes", "nos próximos dias"
            ],
            "saudacao": ["Bom dia", "Boa tarde", "Olá", "Prezado {dest_nome}"],
            "assunto": [
                "Reunião sobre Projeto de Automação",
                "Agendamento de Reunião Técnica",
                "Reunião de Alinhamento",
                "Solicitação de Reunião",
                "Reunião sobre Andamento do Projeto"
            ]
        }
    },
    
    # Solicitações de relatórios/documentação
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: Miguel Jeronimo <miguel.jeronimo@autou.com>
Assunto: {assunto}

{nome},

{saudacao}. Preciso solicitar {documento} sobre {sistema}.

O documento deve conter:
- {requisito1}
- {requisito2}
- {requisito3}
- {requisito4}

{contexto}

Preciso receber até {prazo}. Por favor, me confirme se é possível atender este prazo.

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "documento": [
                "um relatório técnico detalhado", "um relatório de performance",
                "uma documentação atualizada", "um relatório de análise",
                "um documento técnico completo"
            ],
            "sistema": [
                "o sistema de automação", "o projeto implementado",
                "o sistema de IA", "a plataforma instalada",
                "os sistemas em operação"
            ],
            "requisito1": [
                "Análise de performance dos últimos meses",
                "Métricas de utilização do sistema",
                "Análise comparativa com indicadores anteriores",
                "Relatório de disponibilidade e uptime",
                "Análise de custos e ROI"
            ],
            "requisito2": [
                "Identificação de gargalos e oportunidades",
                "Recomendações de melhorias",
                "Análise de riscos e mitigação",
                "Plano de manutenção preventiva",
                "Análise de escalabilidade"
            ],
            "requisito3": [
                "Gráficos e visualizações",
                "Comparativos de performance",
                "Análise de tendências",
                "Projeções futuras",
                "Benchmarks do setor"
            ],
            "requisito4": [
                "Próximos passos recomendados",
                "Plano de ação",
                "Cronograma de implementação",
                "Investimentos necessários",
                "Roadmap de evolução"
            ],
            "contexto": [
                "Este documento será apresentado na reunião do conselho executivo.",
                "Precisamos para nossa reunião trimestral de resultados.",
                "A diretoria solicitou uma análise detalhada.",
                "Será utilizado para planejamento estratégico.",
                "Precisamos para apresentação aos stakeholders."
            ],
            "prazo": [
                "o dia 20 deste mês", "o final desta semana",
                "o dia 25 deste mês", "até sexta-feira",
                "o início da próxima semana"
            ],
            "saudacao": ["Bom dia", "Boa tarde", "Olá", "Prezado Miguel"],
            "assunto": [
                "Solicitação de Relatório Técnico",
                "Solicitação de Documentação",
                "Relatório de Performance Solicitado",
                "Solicitação de Análise Técnica",
                "Documentação Técnica Solicitada"
            ]
        }
    },
    
    # Dúvidas técnicas
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: Miguel Jeronimo <miguel.jeronimo@autou.com>
Assunto: {assunto}

{nome},

{saudacao}. Tenho uma dúvida técnica sobre {topico}.

Especificamente:
- {duvida1}
- {duvida2}
- {duvida3}

{contexto}

Podemos agendar uma call técnica {prazo} para discutir?

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "topico": [
                "a integração do sistema", "a configuração atual",
                "a arquitetura implementada", "o funcionamento do sistema",
                "a integração com sistemas legados"
            ],
            "duvida1": [
                "Como funciona a sincronização de dados?",
                "Qual a capacidade máxima do sistema?",
                "Como é feita a integração com o ERP?",
                "Qual o processo de atualização?",
                "Como funciona o sistema de backup?"
            ],
            "duvida2": [
                "Há limitações que precisamos conhecer?",
                "Quais são os requisitos de infraestrutura?",
                "Como escalar o sistema?",
                "Qual a política de versionamento?",
                "Como é feita a gestão de acessos?"
            ],
            "duvida3": [
                "Precisamos fazer algum ajuste?",
                "Há documentação adicional disponível?",
                "Qual o suporte disponível?",
                "Como reportar problemas?",
                "Quais são as melhores práticas?"
            ],
            "contexto": [
                "Precisamos entender melhor antes de tomar decisões.",
                "Estamos planejando uma atualização e precisamos esclarecer.",
                "A equipe técnica tem algumas questões.",
                "Precisamos alinhar alguns pontos técnicos.",
                "Há algumas questões que precisam ser esclarecidas."
            ],
            "prazo": [
                "esta semana", "na próxima semana", "o quanto antes", "nos próximos dias"
            ],
            "saudacao": ["Bom dia", "Boa tarde", "Olá", "Prezado {dest_nome}"],
            "assunto": [
                "Dúvida Técnica - Integração de Sistemas",
                "Questão Técnica sobre o Sistema",
                "Dúvida sobre Configuração",
                "Pergunta Técnica",
                "Esclarecimento Técnico Necessário"
            ]
        }
    },
    
    # Emails produtivos que começam com agradecimentos (casos difíceis)
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: Miguel Jeronimo <miguel.jeronimo@autou.com>
Assunto: {assunto}

{saudacao}. {agradecimento} pelo {motivo_agradecimento}.

{transicao} {solicitacao}

{contexto}

{acao_requerida}

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "agradecimento": [
                "Muito obrigado", "Obrigado", "Agradeço", "Agradecemos",
                "Muito obrigada", "Agradeço muito"
            ],
            "motivo_agradecimento": [
                "o suporte prestado", "a rápida resposta", "o trabalho realizado",
                "a ajuda anterior", "a atenção dada", "o suporte técnico"
            ],
            "transicao": [
                "Porém,", "No entanto,", "Mas", "Agora", "Agora preciso",
                "Gostaria de", "Preciso", "Seria possível"
            ],
            "solicitacao": [
                "preciso de suporte técnico urgente. O sistema está apresentando falhas críticas.",
                "gostaria de solicitar uma reunião para discutirmos a expansão do projeto.",
                "preciso que você me envie o relatório técnico até o final desta semana.",
                "gostaria de agendar uma call para esclarecer algumas dúvidas técnicas.",
                "preciso de informações sobre o orçamento para o próximo trimestre.",
                "gostaria de solicitar uma atualização do sistema com novas funcionalidades.",
                "preciso de acesso à área de relatórios que ainda está bloqueada.",
                "gostaria de discutir a implementação de melhorias no sistema atual."
            ],
            "contexto": [
                "Isso é urgente pois está impactando nossa operação.",
                "Preciso dessas informações para apresentar ao board.",
                "A situação requer atenção imediata.",
                "Precisamos tomar uma decisão estratégica.",
                "Isso é crítico para nossa operação.",
                "Preciso incluir no planejamento do próximo trimestre."
            ],
            "acao_requerida": [
                "Por favor, entre em contato o mais rápido possível.",
                "Podemos agendar para esta semana?",
                "Preciso receber até sexta-feira.",
                "Seria possível agendarmos uma reunião?",
                "Por favor, me envie as informações solicitadas.",
                "Preciso de uma resposta urgente."
            ],
            "saudacao": ["Bom dia", "Boa tarde", "Olá", "Prezado Miguel"],
            "assunto": [
                "Agradecimento e Solicitação de Suporte",
                "Obrigado e Solicitação Urgente",
                "Agradecimento e Pedido de Informações",
                "Obrigado e Solicitação de Reunião",
                "Agradecimento e Solicitação Técnica"
            ]
        }
    },
    
    # Problemas urgentes
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: Miguel Jeronimo <miguel.jeronimo@autou.com>
Assunto: URGENTE - {problema}

Miguel,

URGENTE! Estamos enfrentando {situacao} no sistema de {sistema}.

Detalhes:
- Local: {local}
- Horário: {horario}
- Erro: {erro}
- Impacto: {impacto}

{descricao}

Precisamos de suporte técnico imediato. Por favor, entre em contato o mais rápido possível.

{nome} {sobrenome}
{cargo}
{empresa}
Tel: {telefone}""",
        "variations": {
            "problema": [
                "Sistema Fora do Ar", "Falha Crítica no Sistema",
                "Problema Urgente", "Sistema com Falhas", "Erro Crítico"
            ],
            "situacao": [
                "uma falha crítica", "um problema grave", "uma situação de emergência",
                "uma falha no sistema", "um erro crítico", "uma parada completa"
            ],
            "sistema": [
                "automação", "automação de produção", "sistema de IA",
                "plataforma de gestão", "sistema de monitoramento"
            ],
            "local": [
                "Fábrica de São Paulo", "Unidade de Produção", "Linha de Produção 3",
                "Centro de Distribuição", "Planta Industrial", "Fábrica Principal"
            ],
            "horario": [
                "desde as 8h desta manhã", "desde o início do turno",
                "nas últimas 2 horas", "desde ontem à noite",
                "durante o turno da noite"
            ],
            "erro": [
                "Falha de comunicação com servidor principal",
                "Erro E-2047 no sistema",
                "Timeout em operações críticas",
                "Sistema não responde",
                "Falha na sincronização de dados"
            ],
            "impacto": [
                "Produção completamente parada",
                "Operação crítica interrompida",
                "Risco de desabastecimento",
                "Perdas financeiras significativas",
                "Impacto direto na produtividade"
            ],
            "descricao": [
                "A produção está completamente parada e precisamos resolver urgentemente.",
                "Estamos com perdas significativas e precisamos de ação imediata.",
                "A situação é crítica e requer atenção imediata da equipe técnica.",
                "O problema está impactando toda a operação e precisamos resolver agora.",
                "Estamos em situação de emergência e precisamos de suporte urgente."
            ]
        }
    }
]

# Templates de emails NÃO PRODUTIVOS (label 0)
UNPRODUCTIVE_TEMPLATES = [
    # Agradecimentos
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: Miguel Jeronimo <miguel.jeronimo@autou.com>
Assunto: {assunto}

{nome},

{saudacao}. Quero {agradecimento} pelo {motivo}.

{elogio}

{reconhecimento}

Muito obrigado pelo {qualidade}!

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "agradecimento": [
                "agradecer", "expressar minha gratidão", "reconhecer",
                "parabenizar", "agradecer pessoalmente"
            ],
            "motivo": [
                "excelente trabalho", "trabalho realizado", "dedicação da equipe",
                "profissionalismo", "suporte prestado", "qualidade do serviço",
                "rapidez na resolução", "comprometimento", "excelência técnica"
            ],
            "elogio": [
                "O trabalho foi excepcional e superou nossas expectativas.",
                "A qualidade técnica foi impressionante.",
                "A equipe demonstrou profissionalismo exemplar.",
                "O resultado foi além do esperado.",
                "A atenção aos detalhes foi notável."
            ],
            "reconhecimento": [
                "Estamos muito satisfeitos com a parceria.",
                "A AutoU se tornou um parceiro estratégico essencial.",
                "Valorizamos muito o trabalho realizado.",
                "A parceria tem sido muito produtiva.",
                "Estamos muito gratos pela colaboração."
            ],
            "qualidade": [
                "trabalho de excelência", "profissionalismo", "dedicação",
                "comprometimento", "qualidade", "excelência"
            ],
            "saudacao": ["Bom dia", "Boa tarde", "Olá", "Prezado Miguel"],
            "assunto": [
                "Agradecimento pelo Excelente Trabalho",
                "Obrigado pelo Profissionalismo",
                "Agradecimento pela Dedicação",
                "Reconhecimento do Trabalho Realizado",
                "Agradecimento"
            ]
        }
    },
    
    # Parabéns e reconhecimentos
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: Miguel Jeronimo <miguel.jeronimo@autou.com>
Assunto: {assunto}

{nome},

{saudacao}. Quero {acao} você e toda a equipe da AutoU pelo {motivo}.

{elogio}

{reconhecimento}

{continuidade}

Parabéns pelo {qualidade}!

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "acao": [
                "parabenizar", "congratular", "reconhecer",
                "felicitar", "celebrar"
            ],
            "motivo": [
                "sucesso do projeto", "excelência técnica", "trabalho excepcional",
                "resultados alcançados", "inovação constante", "aniversário da empresa",
                "conquistas do ano", "excelência demonstrada"
            ],
            "elogio": [
                "Os resultados superaram todas as expectativas.",
                "A qualidade técnica é impressionante.",
                "O trabalho realizado foi exemplar.",
                "A inovação constante é admirável.",
                "A excelência é evidente em todos os projetos."
            ],
            "reconhecimento": [
                "A parceria tem sido fundamental para nossos avanços.",
                "A AutoU se tornou referência em excelência técnica.",
                "Estamos muito satisfeitos com a colaboração.",
                "A qualidade do trabalho é sempre excepcional.",
                "A dedicação da equipe é notável."
            ],
            "continuidade": [
                "Desejamos muito sucesso e crescimento contínuo!",
                "Que continuem sendo referência em inovação!",
                "Estamos ansiosos pelos próximos projetos!",
                "Que continuem alcançando grandes conquistas!",
                "Desejamos muito sucesso nos próximos anos!"
            ],
            "qualidade": [
                "trabalho de excelência", "sucesso", "dedicação",
                "inovação", "excelência técnica"
            ],
            "saudacao": ["Bom dia", "Boa tarde", "Olá", "Prezado Miguel"],
            "assunto": [
                "Parabéns pelo Sucesso do Projeto",
                "Reconhecimento pela Excelência",
                "Parabéns pela Inovação",
                "Reconhecimento do Trabalho",
                "Parabéns!"
            ]
        }
    },
    
    # Felicitações de datas comemorativas
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: Miguel Jeronimo <miguel.jeronimo@autou.com>
Assunto: {assunto}

{nome},

{saudacao}. Desejo a você e toda a equipe da AutoU {desejo}!

{contexto}

{reconhecimento}

{continuidade}

{despedida}

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "desejo": [
                "um Feliz Natal e um Próspero Ano Novo",
                "um excelente 2026",
                "um Feliz Ano Novo",
                "um excelente final de ano",
                "um Feliz Natal"
            ],
            "contexto": [
                "Que este período seja de descanso, reflexão e renovação de energias.",
                "Que este novo ano traga ainda mais sucessos e inovações.",
                "Estamos muito gratos pela parceria ao longo deste ano.",
                "O ano foi marcante para nossa parceria.",
                "Que este período seja de celebração e renovação."
            ],
            "reconhecimento": [
                "A parceria entre {empresa} e AutoU tem sido fundamental.",
                "Estamos muito satisfeitos com a colaboração.",
                "O trabalho realizado foi excepcional.",
                "A qualidade da parceria é notável.",
                "Valorizamos muito a relação estabelecida."
            ],
            "continuidade": [
                "Estamos ansiosos pelos projetos que temos pela frente.",
                "Desejamos muito sucesso e crescimento contínuo.",
                "Que continuem sendo referência em inovação.",
                "Estamos confiantes de que será um ano ainda melhor.",
                "Que continuem alcançando grandes conquistas."
            ],
            "despedida": [
                "Feliz Natal e um excelente 2026!",
                "Desejo muito sucesso, saúde e felicidade!",
                "Um abraço e sucesso!",
                "Desejo muito sucesso para você e toda a equipe!",
                "Feliz Ano Novo!"
            ],
            "saudacao": ["Bom dia", "Boa tarde", "Olá", "Prezado Miguel"],
            "assunto": [
                "Feliz Natal e Próspero Ano Novo",
                "Feliz 2026",
                "Boas Festas",
                "Feliz Ano Novo",
                "Felicitações de Final de Ano"
            ]
        }
    },
    
    # Mensagens informativas sem ação
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: Miguel Jeronimo <miguel.jeronimo@autou.com>
Assunto: {assunto}

{nome},

{saudacao}. Apenas para {informacao}.

{contexto}

{status}

{continuidade}

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "informacao": [
                "informar", "compartilhar", "comunicar",
                "atualizar", "notificar"
            ],
            "contexto": [
                "O projeto está seguindo conforme o planejado.",
                "Todos os sistemas estão operando normalmente.",
                "A equipe está muito satisfeita com os resultados.",
                "Os indicadores estão dentro do esperado.",
                "Tudo está funcionando perfeitamente."
            ],
            "status": [
                "Não há necessidade de ação imediata.",
                "Apenas mantendo você informado.",
                "Tudo está sob controle.",
                "Não há pendências no momento.",
                "Situação está normal."
            ],
            "continuidade": [
                "Mantendo você informado sobre o andamento.",
                "Continuaremos monitorando a situação.",
                "Seguiremos com o planejamento estabelecido.",
                "Manteremos a comunicação regular.",
                "Continuaremos com o trabalho conforme planejado."
            ],
            "saudacao": ["Bom dia", "Boa tarde", "Olá", "Prezado {dest_nome}"],
            "assunto": [
                "Atualização de Status",
                "Informação sobre o Projeto",
                "Comunicação de Status",
                "Atualização",
                "Informação"
            ]
        }
    },
    
    # Confirmações de recebimento
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: {dest_nome} {dest_sobrenome} <{dest_email}>
Assunto: {assunto}

{nome},

{saudacao}. Apenas para {confirmacao} o recebimento do {item}.

{reconhecimento}

{continuidade}

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "confirmacao": [
                "confirmar", "informar", "comunicar",
                "notificar", "registrar"
            ],
            "item": [
                "relatório enviado", "documentação recebida",
                "proposta recebida", "material enviado",
                "informações compartilhadas"
            ],
            "reconhecimento": [
                "Agradecemos pelo envio.",
                "Recebemos e analisaremos.",
                "Obrigado pela documentação.",
                "Agradecemos pela informação.",
                "Recebemos com sucesso."
            ],
            "continuidade": [
                "Retornaremos em breve com nosso feedback.",
                "Analisaremos e retornaremos em breve.",
                "Manteremos você informado.",
                "Seguiremos com a análise.",
                "Continuaremos o processo."
            ],
            "saudacao": ["Bom dia", "Boa tarde", "Olá", "Prezado {dest_nome}"],
            "assunto": [
                "Confirmação de Recebimento",
                "Recebimento Confirmado",
                "Confirmação",
                "Recebido",
                "Confirmação de Recebimento do Material"
            ]
        }
    },
    
    # NEUTRALIZAÇÃO DE PALAVRAS-CHAVE (Anti-Bias) - LABEL_0 com palavras produtivas em contextos informativos
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: {dest_nome} {dest_sobrenome} <{dest_email}>
Assunto: {assunto}

{nome},

{saudacao}. Apenas para {informacao} sobre o {sistema}.

{contexto_informativo}

{status_sem_acao}

{continuidade_informativa}

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "informacao": [
                "informar", "comunicar", "atualizar", "notificar", "compartilhar"
            ],
            "sistema": [
                "sistema de automação", "sistema de IA", "sistema instalado",
                "plataforma de gestão", "sistema de monitoramento", "sistema atual"
            ],
            "contexto_informativo": [
                "O sistema está funcionando perfeitamente e não requer nenhuma ação.",
                "A atualização foi concluída com sucesso e tudo está operacional.",
                "O sistema está estável e não há necessidade de intervenção.",
                "Todas as funcionalidades estão operando normalmente.",
                "O sistema está em pleno funcionamento e sem problemas."
            ],
            "status_sem_acao": [
                "Não há necessidade de suporte técnico no momento.",
                "Não precisamos de nenhuma atualização urgente.",
                "Não há problemas que requeiram atenção imediata.",
                "Não precisamos de nenhuma ação por enquanto.",
                "Tudo está funcionando sem necessidade de intervenção."
            ],
            "continuidade_informativa": [
                "Apenas mantendo você informado sobre o status.",
                "Continuaremos monitorando, mas sem necessidade de ação.",
                "Seguiremos com o funcionamento normal do sistema.",
                "Mantendo você atualizado sobre a operação.",
                "Informação apenas para conhecimento."
            ],
            "saudacao": ["Bom dia", "Boa tarde", "Olá", "Prezado {dest_nome}"],
            "assunto": [
                "Atualização sobre o Sistema",
                "Informação sobre o Sistema de Automação",
                "Status do Sistema",
                "Atualização do Sistema",
                "Informação sobre Sistema"
            ]
        }
    },
    
    # NEUTRALIZAÇÃO: Agradecimento com palavras produtivas mas sem solicitação
    {
        "template": """De: {nome} {sobrenome} <{email}>
Para: {dest_nome} {dest_sobrenome} <{dest_email}>
Assunto: {assunto}

{nome},

{saudacao}. {agradecimento} pela {motivo_agradecimento}.

{reconhecimento_simples}

{continuidade_agradecimento}

Atenciosamente,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "agradecimento": [
                "Muito obrigado", "Obrigado", "Agradeço", "Agradecemos",
                "Muito obrigada", "Agradeço muito"
            ],
            "motivo_agradecimento": [
                "atualização do sistema realizada",
                "suporte técnico prestado anteriormente",
                "sistema que está funcionando perfeitamente",
                "urgência com que resolveram o problema anterior",
                "atualização que foi implementada com sucesso",
                "sistema que está operando sem problemas"
            ],
            "reconhecimento_simples": [
                "O sistema está funcionando muito bem.",
                "Tudo está operando conforme esperado.",
                "Estamos muito satisfeitos com o resultado.",
                "A parceria tem sido excelente.",
                "O trabalho realizado foi impecável."
            ],
            "continuidade_agradecimento": [
                "Não há necessidade de nenhuma ação adicional.",
                "Apenas agradecendo pelo trabalho realizado.",
                "Continuaremos utilizando o sistema normalmente.",
                "Mantendo você informado sobre nossa satisfação.",
                "Sem necessidade de nenhuma intervenção."
            ],
            "saudacao": ["Bom dia", "Boa tarde", "Olá", "Prezado {dest_nome}"],
            "assunto": [
                "Agradecimento pela Atualização",
                "Obrigado pelo Sistema",
                "Agradecimento pelo Suporte",
                "Obrigado pela Atualização do Sistema",
                "Agradecimento"
            ]
        }
    }
]

# Versões em inglês dos templates
PRODUCTIVE_TEMPLATES_EN = [
    {
        "template": """From: {nome} {sobrenome} <{email}>
To: {dest_nome} {dest_sobrenome} <{dest_email}>
Subject: {assunto}

{nome},

{saudacao}. We are experiencing {problema} in the {sistema} system installed at {localizacao}.

Problem details:
- {detalhe1}
- {detalhe2}
- {detalhe3}

This is impacting our operation and we need technical support {urgencia}. Please contact us as soon as possible.

Best regards,
{nome} {sobrenome}
{cargo}
{empresa}
Tel: {telefone}""",
        "variations": {
            "problema": [
                "a critical problem", "intermittent failures", "communication errors",
                "performance issues", "system failures", "synchronization errors",
                "integration problems", "authentication failures", "processing errors"
            ],
            "sistema": [
                "automation", "production automation", "AI system", "quality system",
                "management platform", "traceability system", "monitoring system"
            ],
            "localizacao": [
                "our factory", "our production unit", "our production line",
                "our distribution center", "our plant", "our unit"
            ],
            "detalhe1": [
                "System showing latency above normal",
                "Errors registered in system log",
                "Communication failures between modules",
                "Timeout in critical operations",
                "High CPU and memory usage"
            ],
            "detalhe2": [
                "Production impacted during peaks",
                "Critical operations interrupted",
                "Data synchronization failing",
                "User interface not responding",
                "Reports not being generated"
            ],
            "detalhe3": [
                "We need urgent investigation",
                "Situation requires immediate attention",
                "Direct impact on productivity",
                "Risk of complete operation shutdown",
                "Specialized technical support needed"
            ],
            "urgencia": [
                "urgently", "as soon as possible", "with priority", "immediately", "urgently"
            ],
            "saudacao": ["Good morning", "Good afternoon", "Hello", "Dear {dest_nome}"],
            "assunto": [
                "URGENT - Problem in Automation System",
                "Technical Support Request - System with Failures",
                "Critical System Problem",
                "Failures in Automation System",
                "Urgent Support Request"
            ]
        }
    }
]

UNPRODUCTIVE_TEMPLATES_EN = [
    {
        "template": """From: {nome} {sobrenome} <{email}>
To: {dest_nome} {dest_sobrenome} <{dest_email}>
Subject: {assunto}

{nome},

{saudacao}. I want to {agradecimento} for the {motivo}.

{elogio}

{reconhecimento}

Thank you very much for the {qualidade}!

Best regards,
{nome} {sobrenome}
{cargo}
{empresa}""",
        "variations": {
            "agradecimento": [
                "thank", "express my gratitude", "recognize",
                "congratulate", "personally thank"
            ],
            "motivo": [
                "excellent work", "work performed", "team dedication",
                "professionalism", "support provided", "service quality",
                "quick resolution", "commitment", "technical excellence"
            ],
            "elogio": [
                "The work was exceptional and exceeded our expectations.",
                "The technical quality was impressive.",
                "The team demonstrated exemplary professionalism.",
                "The result was beyond expected.",
                "The attention to detail was remarkable."
            ],
            "reconhecimento": [
                "We are very satisfied with the partnership.",
                "AutoU has become an essential strategic partner.",
                "We greatly value the work performed.",
                "The partnership has been very productive.",
                "We are very grateful for the collaboration."
            ],
            "qualidade": [
                "excellent work", "professionalism", "dedication",
                "commitment", "quality", "excellence"
            ],
            "saudacao": ["Good morning", "Good afternoon", "Hello", "Dear {dest_nome}"],
            "assunto": [
                "Thank You for the Excellent Work",
                "Thanks for the Professionalism",
                "Thank You for the Dedication",
                "Recognition of Work Performed",
                "Thank You"
            ]
        }
    }
]


def generate_email_variations(template_dict: Dict, num_variations: int = 5) -> List[str]:
    """Gera variações de um template de email."""
    emails = []
    template = template_dict["template"]
    variations = template_dict["variations"]
    
    for _ in range(num_variations):
        # Seleciona valores aleatórios para cada campo
        filled_template = template
        for key, value_list in variations.items():
            if isinstance(value_list, list):
                value = random.choice(value_list)
                filled_template = filled_template.replace(f"{{{key}}}", value)
        
        emails.append(filled_template)
    
    return emails


def generate_random_person() -> tuple:
    """Gera uma pessoa aleatória com nome, email e cargo."""
    nome = random.choice(NOMES)
    sobrenome = random.choice(SOBRENOMES)
    empresa, dominio = random.choice(CLIENTES)
    email = f"{nome.lower()}.{sobrenome.lower()}@{dominio}"
    cargo = random.choice(CARGOS)
    telefone = f"(11) {random.randint(10000, 99999)}-{random.randint(1000, 9999)}"
    
    return nome, sobrenome, email, cargo, empresa, telefone


def generate_random_recipient() -> tuple:
    """Gera um destinatário aleatório para evitar data leakage (não usa 'Miguel' fixo)."""
    nome = random.choice(NOMES)
    sobrenome = random.choice(SOBRENOMES)
    # Gera email da AutoU com nome aleatório
    email = f"{nome.lower()}.{sobrenome.lower()}@autou.com"
    
    return nome, sobrenome, email


def inject_negation(text: str, probability: float = 0.3) -> str:
    """Injeta negações antes de palavras de ação para criar variações anti-bias."""
    if random.random() > probability:
        return text
    
    # Padrões de palavras de ação que podem ser negadas
    action_patterns = [
        (r'\bpreciso\s+de\s+atualização\b', 'não preciso de atualização'),
        (r'\bprecisamos\s+de\s+atualização\b', 'não precisamos de atualização'),
        (r'\bpreciso\s+urgente\b', 'não preciso urgente'),
        (r'\bprecisamos\s+urgente\b', 'não precisamos urgente'),
        (r'\bpreciso\s+de\s+suporte\b', 'não preciso de suporte'),
        (r'\bprecisamos\s+de\s+suporte\b', 'não precisamos de suporte'),
        (r'\bpreciso\s+de\s+informações\b', 'não preciso de informações'),
        (r'\bprecisamos\s+de\s+informações\b', 'não precisamos de informações'),
        (r'\bpreciso\s+de\s+reunião\b', 'não preciso de reunião'),
        (r'\bprecisamos\s+de\s+reunião\b', 'não precisamos de reunião'),
        (r'\bcom\s+urgência\b', 'sem urgência'),
        (r'\bcom\s+prioridade\b', 'sem prioridade'),
        (r'\brequer\s+atenção\b', 'não requer atenção'),
        (r'\brequer\s+ação\b', 'não requer ação'),
        (r'\bprecisa\s+de\s+atualização\b', 'não precisa de atualização'),
        (r'\bprecisa\s+urgente\b', 'não precisa urgente'),
    ]
    
    modified_text = text
    for pattern, replacement in action_patterns:
        if re.search(pattern, modified_text, re.IGNORECASE):
            # Aplica negação com probabilidade
            if random.random() < 0.5:
                modified_text = re.sub(pattern, replacement, modified_text, flags=re.IGNORECASE)
    
    return modified_text


def shuffle_context_parts(text: str) -> str:
    """Embaralha partes do contexto (agradecimento, solicitação, informação) para evitar overfitting posicional."""
    # Divide o texto em parágrafos
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    if len(paragraphs) < 2:
        return text
    
    # Identifica tipos de parágrafos
    gratitude_paragraphs = []
    request_paragraphs = []
    info_paragraphs = []
    other_paragraphs = []
    
    gratitude_keywords = ['obrigado', 'obrigada', 'agradeço', 'agradecemos', 'valeu', 'grato', 'grata']
    request_keywords = ['preciso', 'gostaria', 'solicito', 'solicitamos', 'por favor', 'poderia', 'seria possível']
    
    for para in paragraphs:
        para_lower = para.lower()
        is_gratitude = any(kw in para_lower for kw in gratitude_keywords)
        is_request = any(kw in para_lower for kw in request_keywords)
        
        if is_gratitude and not is_request:
            gratitude_paragraphs.append(para)
        elif is_request:
            request_paragraphs.append(para)
        elif any(kw in para_lower for kw in ['informar', 'comunicar', 'atualizar', 'status', 'situação']):
            info_paragraphs.append(para)
        else:
            other_paragraphs.append(para)
    
    # Embaralha a ordem: pode colocar agradecimento antes, depois ou no meio
    if gratitude_paragraphs and (request_paragraphs or info_paragraphs):
        shuffle_type = random.choice(['before', 'after', 'middle', 'mixed'])
        
        if shuffle_type == 'before':
            # Agradecimento primeiro
            final_order = gratitude_paragraphs + request_paragraphs + info_paragraphs + other_paragraphs
        elif shuffle_type == 'after':
            # Agradecimento por último
            final_order = request_paragraphs + info_paragraphs + other_paragraphs + gratitude_paragraphs
        elif shuffle_type == 'middle':
            # Agradecimento no meio
            mid_point = len(request_paragraphs + info_paragraphs) // 2
            all_paras = request_paragraphs + info_paragraphs + other_paragraphs
            final_order = all_paras[:mid_point] + gratitude_paragraphs + all_paras[mid_point:]
        else:  # mixed
            # Embaralha tudo aleatoriamente
            all_paras = gratitude_paragraphs + request_paragraphs + info_paragraphs + other_paragraphs
            random.shuffle(all_paras)
            final_order = all_paras
        
        return '\n\n'.join(final_order)
    
    return text


def extract_email_body(email_text: str) -> str:
    """Extrai apenas o corpo do email, removendo cabeçalhos (De:, Para:, Assunto:)."""
    lines = email_text.split('\n')
    body_started = False
    body_lines = []
    
    for line in lines:
        line_lower = line.lower().strip()
        # Detecta início do corpo (primeira linha vazia após cabeçalhos)
        if not body_started:
            if line.strip() == "":
                body_started = True
            elif line_lower.startswith(('de:', 'from:', 'para:', 'to:', 'assunto:', 'subject:')):
                continue  # Pula cabeçalhos
            else:
                # Se não é cabeçalho nem linha vazia, pode ser o início do corpo
                body_started = True
                body_lines.append(line)
        else:
            body_lines.append(line)
    
    body = '\n'.join(body_lines).strip()
    # Se não encontrou corpo, retorna tudo (caso de emails sem cabeçalhos)
    return body if body else email_text


def invert_email_order(text: str) -> str:
    """Inverte a ordem do email, colocando solicitação antes do agradecimento."""
    # Padrões comuns de agradecimento
    gratitude_keywords = [
        'obrigado', 'obrigada', 'agradeço', 'agradecemos', 'valeu',
        'muito obrigado', 'muito obrigada', 'agradecimento', 'grato', 'grata'
    ]
    
    # Padrões de solicitação
    request_keywords = [
        'preciso', 'gostaria', 'solicito', 'quero', 'precisamos',
        'gostaríamos', 'solicitamos', 'poderia', 'seria possível',
        'por favor', 'precisamos de', 'gostaria de', 'solicito que'
    ]
    
    # Divide em sentenças (considera múltiplos delimitadores)
    sentences = re.split(r'[.!?]\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 2:
        return text  # Não inverte se muito curto
    
    # Identifica sentenças de agradecimento e solicitação
    gratitude_sentences = []
    request_sentences = []
    other_sentences = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        
        # Verifica se é agradecimento
        is_gratitude = any(keyword in sentence_lower for keyword in gratitude_keywords)
        # Verifica se é solicitação
        is_request = any(keyword in sentence_lower for keyword in request_keywords)
        
        if is_gratitude and not is_request:
            gratitude_sentences.append(sentence)
        elif is_request:
            request_sentences.append(sentence)
        else:
            other_sentences.append(sentence)
    
    # Se encontrou ambos, inverte a ordem
    if gratitude_sentences and request_sentences:
        # Coloca solicitação primeiro, depois outras sentenças, depois agradecimento
        new_order = request_sentences + other_sentences + gratitude_sentences
        return '. '.join(new_order) + '.' if new_order else text
    
    return text


def generate_gratitude_with_request_emails(num_emails: int = 500) -> List[Dict]:
    """Gera emails que começam com agradecimento mas terminam com solicitação."""
    emails = []
    
    greetings = ["Valeu", "Obrigado", "Obrigada", "Muito obrigado", "Muito obrigada", "Bom dia", "Boa tarde"]
    
    gratitude_phrases = [
        "pelo suporte prestado",
        "pela ajuda anterior",
        "pela rápida resposta",
        "pelo trabalho realizado",
        "pela atenção dada",
        "pelo suporte técnico",
        "pela dedicação",
        "pelo profissionalismo"
    ]
    
    requests = [
        "Preciso de suporte técnico urgente. O sistema está apresentando falhas críticas. Podemos resolver isso hoje?",
        "Gostaria de agendar uma reunião para discutir a expansão do projeto. Quando você está disponível?",
        "Preciso que você me envie o relatório técnico até o final desta semana. Seria possível?",
        "Gostaria de agendar uma call para esclarecer algumas dúvidas técnicas. Qual horário funciona melhor?",
        "Preciso de informações sobre o orçamento para o próximo trimestre. Podemos conversar esta semana?",
        "Gostaria de solicitar uma atualização do sistema com novas funcionalidades. Quando podemos iniciar?",
        "Preciso de acesso à área de relatórios que ainda está bloqueada. Podemos resolver isso agora?",
        "Gostaria de discutir a implementação de melhorias no sistema atual. Podemos agendar uma reunião?",
        "Preciso de suporte para configurar uma nova funcionalidade. Você tem disponibilidade hoje?",
        "Gostaria de solicitar uma análise técnica do sistema. Quando podemos agendar?",
        "Preciso de ajuda para resolver um problema crítico. Podemos conversar o quanto antes?",
        "Gostaria de solicitar uma demonstração das novas funcionalidades. Quando seria possível?",
        "Preciso de informações técnicas sobre a integração. Podemos agendar uma call?",
        "Gostaria de solicitar um treinamento para a equipe. Quando podemos agendar?",
        "Preciso de suporte para migração de dados. Podemos iniciar esta semana?",
        "Gostaria de solicitar uma proposta para expansão do projeto. Quando podemos discutir?",
        "Preciso de acesso ao ambiente de testes. Podemos configurar hoje?",
        "Gostaria de solicitar uma documentação atualizada. Quando você pode enviar?",
        "Preciso de suporte para resolver um erro no sistema. Podemos conversar agora?",
        "Gostaria de agendar uma reunião de alinhamento. Qual dia funciona melhor?"
    ]
    
    transitions = [
        "Porém,", "No entanto,", "Mas", "Agora", "Agora preciso",
        "Gostaria de", "Preciso", "Seria possível", "Queria",
        "Também preciso", "Além disso, preciso"
    ]
    
    for _ in range(num_emails):
        greeting = random.choice(greetings)
        gratitude = random.choice(gratitude_phrases)
        transition = random.choice(transitions)
        request = random.choice(requests)
        
        # Varia a estrutura
        if random.random() < 0.5:
            # Estrutura: Saudação + Agradecimento + Transição + Solicitação
            text = f"{greeting}! {random.choice(['Muito obrigado', 'Obrigado', 'Agradeço'])} {gratitude}. {transition} {request}"
        else:
            # Estrutura: Saudação + Agradecimento. Solicitação direta
            text = f"{greeting}! {random.choice(['Muito obrigado', 'Obrigado', 'Agradeço'])} {gratitude}. {request}"
        
        # Remove cabeçalhos se houver
        body_text = extract_email_body(text)
        # Adiciona ruído ocasionalmente
        body_text = add_noise_to_text(body_text, noise_probability=0.1)
        
        emails.append({
            "text": body_text,
            "label": 1  # Produtivo (tem solicitação)
        })
    
    return emails


def add_noise_to_text(text: str, noise_probability: float = 0.1) -> str:
    """Adiciona ruído ao texto para tornar os dados mais realistas."""
    if random.random() > noise_probability:
        return text
    
    lines = text.split('\n')
    noisy_lines = []
    
    for line in lines:
        if not line.strip():
            noisy_lines.append(line)
            continue
        
        # Adiciona pequenos erros de digitação ocasionais
        words = line.split()
        noisy_words = []
        
        for word in words:
            if random.random() < 0.02 and len(word) > 3:  # 2% de chance de erro por palavra
                # Troca letras adjacentes
                if len(word) > 4:
                    idx = random.randint(0, len(word) - 2)
                    word = word[:idx] + word[idx+1] + word[idx] + word[idx+2:]
            noisy_words.append(word)
        
        noisy_line = ' '.join(noisy_words)
        noisy_lines.append(noisy_line)
    
    return '\n'.join(noisy_lines)


def fill_template_variables(template: str, variations: Dict) -> str:
    """Preenche as variáveis de um template com valores aleatórios."""
    nome, sobrenome, email, cargo, empresa, telefone = generate_random_person()
    dest_nome, dest_sobrenome, dest_email = generate_random_recipient()
    
    # Preenche variáveis fixas do remetente
    filled = template.replace("{nome}", nome)
    filled = filled.replace("{sobrenome}", sobrenome)
    filled = filled.replace("{email}", email)
    filled = filled.replace("{cargo}", cargo)
    filled = filled.replace("{empresa}", empresa)
    filled = filled.replace("{telefone}", telefone)
    
    # Preenche variáveis do destinatário (evita data leakage)
    filled = filled.replace("{dest_nome}", dest_nome)
    filled = filled.replace("{dest_sobrenome}", dest_sobrenome)
    filled = filled.replace("{dest_email}", dest_email)
    
    # Preenche variáveis de variação (pode conter {dest_nome} nas saudações)
    for key, value_list in variations.items():
        if isinstance(value_list, list) and len(value_list) > 0:
            value = random.choice(value_list)
            # Substitui {dest_nome} nas variações também
            value = value.replace("{dest_nome}", dest_nome)
            filled = filled.replace(f"{{{key}}}", value)
        elif isinstance(value_list, str):
            value = value_list.replace("{dest_nome}", dest_nome)
            filled = filled.replace(f"{{{key}}}", value)
    
    return filled


def generate_productive_emails(num_emails: int, invert_order_probability: float = 0.3) -> List[Dict]:
    """Gera emails produtivos com inversão de ordem ocasional."""
    emails = []
    templates_per_category = num_emails // len(PRODUCTIVE_TEMPLATES)
    
    for template_dict in PRODUCTIVE_TEMPLATES:
        for _ in range(templates_per_category):
            email_text = fill_template_variables(
                template_dict["template"],
                template_dict["variations"]
            )
            # Remove cabeçalhos e mantém apenas o corpo
            body_text = extract_email_body(email_text)
            
            # Embaralha contexto (agradecimento pode vir antes, depois ou no meio)
            if random.random() < 0.4:  # 40% dos casos
                body_text = shuffle_context_parts(body_text)
            
            # Inverte a ordem ocasionalmente (30% dos casos)
            if random.random() < invert_order_probability:
                body_text = invert_email_order(body_text)
            
            # Adiciona ruído ocasionalmente
            body_text = add_noise_to_text(body_text, noise_probability=0.15)
            
            emails.append({
                "text": body_text,
                "label": 1  # Produtivo
            })
    
    # Adiciona emails em inglês
    for template_dict in PRODUCTIVE_TEMPLATES_EN:
        for _ in range(templates_per_category // 2):
            email_text = fill_template_variables(
                template_dict["template"],
                template_dict["variations"]
            )
            body_text = extract_email_body(email_text)
            
            # Embaralha contexto
            if random.random() < 0.4:
                body_text = shuffle_context_parts(body_text)
            
            # Inverte a ordem ocasionalmente
            if random.random() < invert_order_probability:
                body_text = invert_email_order(body_text)
            
            body_text = add_noise_to_text(body_text, noise_probability=0.15)
            
            emails.append({
                "text": body_text,
                "label": 1  # Produtivo
            })
    
    # Preenche até o número desejado
    while len(emails) < num_emails:
        template_dict = random.choice(PRODUCTIVE_TEMPLATES)
        email_text = fill_template_variables(
            template_dict["template"],
            template_dict["variations"]
        )
        body_text = extract_email_body(email_text)
        
        # Embaralha contexto
        if random.random() < 0.4:
            body_text = shuffle_context_parts(body_text)
        
        # Inverte a ordem ocasionalmente
        if random.random() < invert_order_probability:
            body_text = invert_email_order(body_text)
        
        body_text = add_noise_to_text(body_text, noise_probability=0.15)
        
        emails.append({
            "text": body_text,
            "label": 1
        })
    
    return emails[:num_emails]


def generate_unproductive_emails(num_emails: int) -> List[Dict]:
    """Gera emails não produtivos com injeção de negação e embaralhamento."""
    emails = []
    templates_per_category = num_emails // len(UNPRODUCTIVE_TEMPLATES)
    
    for template_dict in UNPRODUCTIVE_TEMPLATES:
        for _ in range(templates_per_category):
            email_text = fill_template_variables(
                template_dict["template"],
                template_dict["variations"]
            )
            # Remove cabeçalhos e mantém apenas o corpo
            body_text = extract_email_body(email_text)
            
            # Aplica injeção de negação (30% dos casos) - palavras produtivas negadas
            if random.random() < 0.3:
                body_text = inject_negation(body_text, probability=0.8)
            
            # Embaralha contexto (agradecimento pode vir antes, depois ou no meio)
            if random.random() < 0.4:  # 40% dos casos
                body_text = shuffle_context_parts(body_text)
            
            # Adiciona ruído ocasionalmente
            body_text = add_noise_to_text(body_text, noise_probability=0.15)
            
            emails.append({
                "text": body_text,
                "label": 0  # Não produtivo
            })
    
    # Adiciona emails em inglês
    for template_dict in UNPRODUCTIVE_TEMPLATES_EN:
        for _ in range(templates_per_category // 2):
            email_text = fill_template_variables(
                template_dict["template"],
                template_dict["variations"]
            )
            body_text = extract_email_body(email_text)
            
            # Aplica injeção de negação (30% dos casos)
            if random.random() < 0.3:
                body_text = inject_negation(body_text, probability=0.8)
            
            # Embaralha contexto
            if random.random() < 0.4:
                body_text = shuffle_context_parts(body_text)
            
            body_text = add_noise_to_text(body_text, noise_probability=0.15)
            
            emails.append({
                "text": body_text,
                "label": 0  # Não produtivo
            })
    
    # Preenche até o número desejado
    while len(emails) < num_emails:
        template_dict = random.choice(UNPRODUCTIVE_TEMPLATES)
        email_text = fill_template_variables(
            template_dict["template"],
            template_dict["variations"]
        )
        body_text = extract_email_body(email_text)
        
        # Aplica injeção de negação (30% dos casos)
        if random.random() < 0.3:
            body_text = inject_negation(body_text, probability=0.8)
        
        # Embaralha contexto
        if random.random() < 0.4:
            body_text = shuffle_context_parts(body_text)
        
        body_text = add_noise_to_text(body_text, noise_probability=0.15)
        
        emails.append({
            "text": body_text,
            "label": 0
        })
    
    return emails[:num_emails]


def generate_training_data(
    num_productive: int = 2000,
    num_unproductive: int = 2000,
    output_file: str = "training_data.json",
    add_gratitude_requests: bool = True,
    num_gratitude_requests: int = 500
) -> None:
    """Gera dados de treinamento com inversão de ordem e casos específicos."""
    print("=" * 60)
    print("Gerador de Dados de Treinamento (Anti-Overfitting)")
    print("=" * 60)
    print(f"\n📧 Gerando {num_productive} emails produtivos...")
    print("   (30% terão ordem invertida: solicitação antes do agradecimento)")
    productive_emails = generate_productive_emails(num_productive, invert_order_probability=0.3)
    
    print(f"\n📧 Gerando {num_unproductive} emails não produtivos...")
    unproductive_emails = generate_unproductive_emails(num_unproductive)
    
    # Adiciona emails específicos que começam com agradecimento mas têm solicitação
    if add_gratitude_requests:
        print(f"\n🎯 Gerando {num_gratitude_requests} emails específicos...")
        print("   (Começam com 'Valeu', 'Obrigado' ou 'Bom dia' mas terminam com solicitação)")
        gratitude_request_emails = generate_gratitude_with_request_emails(num_gratitude_requests)
        productive_emails.extend(gratitude_request_emails)
        print(f"   ✓ Adicionados {len(gratitude_request_emails)} emails ao conjunto produtivo")
    
    # Combina e embaralha
    all_emails = productive_emails + unproductive_emails
    random.shuffle(all_emails)
    
    # Salva em JSON
    print(f"\n💾 Salvando {len(all_emails)} emails em {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_emails, f, ensure_ascii=False, indent=2)
    
    # Estatísticas
    from collections import Counter
    label_counts = Counter(email["label"] for email in all_emails)
    
    print("\n" + "=" * 60)
    print("📊 Estatísticas:")
    print("=" * 60)
    print(f"Total de emails gerados: {len(all_emails)}")
    print(f"  - Produtivos (label 1): {label_counts[1]}")
    print(f"  - Não produtivos (label 0): {label_counts[0]}")
    if add_gratitude_requests:
        print(f"  - Emails com agradecimento + solicitação: {num_gratitude_requests}")
    print(f"\n💾 Arquivo salvo em: {output_file}")
    print("\n✅ Geração de dados concluída!")
    print("\n💡 Melhorias Anti-Overfitting e Data Leakage Prevention aplicadas:")
    print("   ✓ Neutralização de Palavras-Chave: Templates LABEL_0 com palavras produtivas")
    print("     (Urgente, Atualização, Sistema) em contextos puramente informativos")
    print("   ✓ Injeção de Negação: 30% dos emails LABEL_0 têm negações antes de ações")
    print("     (ex: 'não precisa de atualização', 'sem urgência')")
    print("   ✓ Data Leakage Prevention: Nomes dinâmicos (removido 'Miguel' fixo)")
    print("     Destinatários gerados aleatoriamente para evitar associações fixas")
    print("   ✓ Embaralhamento de Contexto: 40% dos emails têm agradecimentos")
    print("     posicionados antes, depois ou no meio das solicitações/informações")
    print("   ✓ 30% dos emails produtivos têm ordem invertida")
    print("   ✓ Modelo aprenderá que posição e palavras isoladas não importam,")
    print("     apenas o contexto e a presença real de solicitações")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gera dados de treinamento para classificação de emails"
    )
    parser.add_argument(
        "--productive",
        type=int,
        default=2000,
        help="Número de emails produtivos a gerar (padrão: 2000)"
    )
    parser.add_argument(
        "--unproductive",
        type=int,
        default=2000,
        help="Número de emails não produtivos a gerar (padrão: 2000)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="training_data.json",
        help="Arquivo de saída (padrão: training_data.json)"
    )
    parser.add_argument(
        "--no-gratitude-requests",
        action="store_true",
        help="Não adicionar emails específicos com agradecimento + solicitação"
    )
    parser.add_argument(
        "--num-gratitude-requests",
        type=int,
        default=500,
        help="Número de emails com agradecimento + solicitação (padrão: 500)"
    )
    
    args = parser.parse_args()
    
    random.seed(42)  # Para reprodutibilidade
    generate_training_data(
        num_productive=args.productive,
        num_unproductive=args.unproductive,
        output_file=args.output,
        add_gratitude_requests=not args.no_gratitude_requests,
        num_gratitude_requests=args.num_gratitude_requests
    )

