"""Script para gerar dados de treinamento complexos e desafiadores com emails técnicos variados em português e inglês."""

import json
import random
import re
import os
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

# Clientes e empresas (expandido)
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
    ("Gerdau", "gerdau.com.br"),
    ("Braskem", "braskem.com"),
    ("Klabin", "klabin.com.br"),
    ("Suzano", "suzano.com.br"),
    ("Raízen", "raizen.com.br"),
    ("Cosan", "cosan.com.br"),
    ("Rumo", "rumolog.com"),
    ("CSN", "csn.com.br"),
    ("ArcelorMittal", "arcelormittal.com"),
    ("Usiminas", "usiminas.com.br"),
]

NOMES_PT = [
    "Miguel", "Ana", "Carlos", "Juliana", "Roberto", "Patricia", "Thiago", "Beatriz",
    "Eduardo", "Camila", "Ricardo", "Amanda", "Paulo", "Larissa", "Lucas", "Sofia",
    "Fernando", "Mariana", "Gabriel", "Isabella", "Rafael", "Renata", "Daniel", "Ana Paula",
    "Roberto", "Carolina", "Henrique", "Vanessa", "André", "Cristina", "Bruno", "Tatiana",
    "Felipe", "Bruna", "Marcelo", "Priscila", "Gustavo", "Fernanda", "Rodrigo", "Juliana"
]

NOMES_EN = [
    "Michael", "Anna", "Charles", "Julia", "Robert", "Patricia", "Thomas", "Beatrice",
    "Edward", "Camila", "Richard", "Amanda", "Paul", "Larissa", "Luke", "Sophia",
    "Fernando", "Mariana", "Gabriel", "Isabella", "Rafael", "Renata", "Daniel", "Anna",
    "Robert", "Caroline", "Henry", "Vanessa", "Andrew", "Christina", "Bruno", "Tatiana",
    "Philip", "Brenda", "Marcelo", "Priscilla", "Gustavo", "Fernanda", "Rodrigo", "Julia",
    "John", "Sarah", "David", "Emily", "James", "Jessica", "William", "Emma"
]

NOMES = NOMES_PT + NOMES_EN

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira",
    "Lima", "Costa", "Rocha", "Martins", "Carvalho", "Almeida", "Lopes", "Fernandes",
    "Araújo", "Mendes", "Torres", "Gomes", "Ribeiro", "Barbosa", "Reis", "Monteiro",
    "Cavalcanti", "Melo", "Azevedo", "Dias", "Cunha", "Ramos", "Moreira", "Freitas"
]

# Termos técnicos variados para evitar overfitting (EXPANDIDO)
TERMOS_TECNICOS = {
    "erros": [
        "erro 500", "erro 404", "erro 503", "erro 502", "erro 401", "erro 403",
        "erro 429", "erro 504", "erro 507", "erro 508", "erro 509", "erro 520",
        "timeout", "connection refused", "gateway timeout", "bad gateway",
        "internal server error", "service unavailable", "unauthorized",
        "forbidden", "not found", "method not allowed", "request timeout",
        "E-2047", "E-3012", "E-4501", "E-5200", "E-6001", "E-7203", "E-8001",
        "E-9002", "E-1003", "E-1104", "E-1205", "E-1306", "E-1407",
        "exception", "stack trace", "segmentation fault", "null pointer",
        "out of memory", "deadlock", "race condition", "buffer overflow",
        "stack overflow", "heap overflow", "integer overflow", "underflow",
        "divide by zero", "invalid pointer", "access violation", "page fault",
        "kernel panic", "blue screen", "segfault", "bus error", "abort signal",
        "SIGSEGV", "SIGBUS", "SIGFPE", "SIGILL", "SIGABRT", "core dump"
    ],
    "sistemas": [
        "sistema de IA", "plataforma de automação", "sistema de monitoramento",
        "API REST", "API GraphQL", "microserviços", "servidor de aplicação",
        "banco de dados", "data warehouse", "data lake", "ETL pipeline",
        "sistema de rastreabilidade", "sistema de qualidade", "dashboard",
        "interface de gestão", "portal web", "aplicativo mobile", "webhook",
        "serviço de mensageria", "fila de processamento", "cache distribuído",
        "load balancer", "reverse proxy", "CDN", "servidor de arquivos",
        "message broker", "event stream", "streaming platform", "batch processor",
        "real-time processor", "scheduler", "cron job", "background worker",
        "task queue", "job queue", "workflow engine", "orchestrator",
        "service mesh", "API gateway", "service registry", "config server",
        "secret manager", "identity provider", "authentication service",
        "authorization service", "audit log", "compliance system", "backup system"
    ],
    "problemas": [
        "latência alta", "throughput baixo", "alta concorrência", "race condition",
        "memory leak", "CPU spike", "disco I/O alto", "network congestion",
        "database lock", "deadlock", "connection pool esgotado", "cache miss",
        "sincronização falhando", "replicação atrasada", "backup falhando",
        "migração travada", "deploy falhando", "build quebrado", "testes falhando",
        "integração quebrada", "autenticação falhando", "autorização negada",
        "token expirado", "sessão inválida", "certificado expirado", "SSL error",
        "handshake failure", "certificate chain invalid", "hostname mismatch",
        "cipher suite mismatch", "protocol version mismatch", "compression error",
        "deflate error", "gzip error", "encoding error", "decoding error",
        "serialization error", "deserialization error", "marshalling error",
        "unmarshalling error", "parsing error", "validation error", "schema mismatch",
        "version mismatch", "compatibility issue", "dependency conflict",
        "circular dependency", "missing dependency", "broken dependency",
        "network partition", "split brain", "consensus failure", "leader election failure",
        "quorum loss", "replication lag", "write conflict", "read conflict",
        "transaction rollback", "transaction timeout", "isolation violation",
        "constraint violation", "foreign key violation", "unique constraint violation",
        "check constraint violation", "not null violation", "data type mismatch",
        "overflow error", "underflow error", "precision loss", "rounding error"
    ],
    "tecnologias": [
        "Kubernetes", "Docker", "AWS", "Azure", "GCP", "Terraform", "Ansible",
        "Jenkins", "GitLab CI", "GitHub Actions", "Prometheus", "Grafana",
        "Elasticsearch", "Kibana", "Logstash", "Redis", "MongoDB", "PostgreSQL",
        "MySQL", "Oracle", "SQL Server", "Cassandra", "Kafka", "RabbitMQ",
        "Nginx", "Apache", "HAProxy", "Istio", "Linkerd", "Consul", "Vault",
        "React", "Vue", "Angular", "Node.js", "Python", "Java", "Go", "Rust",
        "Spring Boot", "Django", "Flask", "FastAPI", "Express", "NestJS",
        "Elixir", "Erlang", "Scala", "Kotlin", "Swift", "TypeScript", "C#",
        "C++", "C", "Ruby", "PHP", "Perl", "Lua", "Haskell", "Clojure",
        "F#", "OCaml", "R", "MATLAB", "Julia", "Fortran", "COBOL", "Assembly",
        "Terraform", "Pulumi", "CloudFormation", "ARM Templates", "Helm",
        "Kustomize", "Skaffold", "Tilt", "Telepresence", "Squash", "Draft",
        "Brigade", "Flux", "Argo", "Tekton", "Spinnaker", "Jenkins X",
        "CircleCI", "Travis CI", "Bamboo", "TeamCity", "Drone", "Concourse",
        "Buildkite", "Codefresh", "Harness", "GitOps", "FluxCD", "ArgoCD"
    ],
    "métricas": [
        "response time", "p95 latency", "p99 latency", "throughput", "QPS",
        "error rate", "availability", "uptime", "downtime", "MTTR", "MTBF",
        "CPU usage", "memory usage", "disk I/O", "network I/O", "connection count",
        "request rate", "cache hit rate", "database query time", "API latency",
        "queue depth", "processing time", "wait time", "idle time",
        "p50 latency", "p90 latency", "p99.9 latency", "p99.99 latency",
        "request duration", "response size", "request size", "payload size",
        "compression ratio", "cache miss rate", "cache eviction rate",
        "garbage collection time", "GC pause time", "heap size", "stack size",
        "thread count", "process count", "file descriptor count", "socket count",
        "active connections", "idle connections", "connection pool size",
        "transaction rate", "commit rate", "rollback rate", "lock wait time",
        "deadlock count", "slow query count", "query execution time",
        "index usage", "table scan count", "buffer pool hit rate",
        "replication lag", "sync delay", "backup duration", "restore duration",
        "deployment duration", "build duration", "test duration", "coverage"
    ],
    "integrações": [
        "integração com Slack", "integração com Teams", "integração com Jira",
        "integração com Salesforce", "integração com SAP", "integração com Oracle",
        "integração com ERP", "integração com CRM", "integração com WMS",
        "integração com TMS", "integração com BI", "integração com Power BI",
        "integração com Tableau", "integração com Google Analytics",
        "integração com AWS S3", "integração com Azure Blob", "integração com GCP Storage",
        "webhook", "REST API", "SOAP API", "GraphQL API", "gRPC", "message queue",
        "integração com Confluence", "integração com Trello", "integração com Asana",
        "integração com Monday", "integração com Notion", "integração com Airtable",
        "integração com HubSpot", "integração com Pipedrive", "integração com Zoho",
        "integração com Mailchimp", "integração com SendGrid", "integração com Twilio",
        "integração com Stripe", "integração com PayPal", "integração com Mercado Pago",
        "integração com PagSeguro", "integração com Pagar.me", "integração com Iugu",
        "integração com AWS Lambda", "integração com Azure Functions", "integração com GCP Functions",
        "integração com AWS SQS", "integração com Azure Service Bus", "integração com GCP Pub/Sub",
        "integração com AWS SNS", "integração com Azure Event Grid", "integração com GCP Cloud Pub/Sub",
        "integração com AWS EventBridge", "integração com Azure Event Hubs", "integração com GCP Cloud Events"
    ],
    "domínios_email": [
        "@gmail.com", "@outlook.com", "@hotmail.com", "@yahoo.com", "@icloud.com",
        "@corporate.com", "@empresa.com.br", "@dominio.com", "@mail.com",
        "@protonmail.com", "@zoho.com", "@yandex.com", "@mail.ru", "@gmx.com",
        "@aol.com", "@live.com", "@msn.com", "@terra.com.br", "@uol.com.br",
        "@bol.com.br", "@ig.com.br", "@globo.com", "@r7.com", "@folha.com.br"
    ],
    "protocolos": [
        "SMTP", "IMAP", "POP3", "HTTP", "HTTPS", "FTP", "SFTP", "SSH", "TCP",
        "UDP", "WebSocket", "gRPC", "AMQP", "MQTT", "Kafka Protocol", "REST",
        "SOAP", "GraphQL", "OAuth", "OAuth2", "JWT", "SAML", "LDAP", "Kerberos",
        "TLS", "SSL", "DTLS", "QUIC", "HTTP/2", "HTTP/3", "WebRTC", "RTSP",
        "RTMP", "HLS", "DASH", "SIP", "RTP", "SRTP", "SCTP", "ICMP", "IGMP",
        "ARP", "RARP", "BGP", "OSPF", "IS-IS", "EIGRP", "RIP", "MPLS", "VXLAN",
        "GRE", "IPsec", "L2TP", "PPTP", "OpenVPN", "WireGuard", "IKEv2"
    ],
    "ambientes": [
        "ambiente de desenvolvimento", "ambiente de staging", "ambiente de produção",
        "ambiente de testes", "ambiente de homologação", "ambiente de QA",
        "ambiente de UAT", "ambiente de sandbox", "ambiente de demo",
        "cluster de desenvolvimento", "cluster de staging", "cluster de produção",
        "namespace de desenvolvimento", "namespace de staging", "namespace de produção",
        "região us-east-1", "região us-west-2", "região eu-west-1", "região sa-east-1",
        "zona de disponibilidade A", "zona de disponibilidade B", "zona de disponibilidade C",
        "datacenter primário", "datacenter secundário", "datacenter de backup",
        "servidor físico", "servidor virtual", "container", "pod", "service",
        "deployment", "statefulset", "daemonset", "job", "cronjob", "configmap",
        "secret", "persistent volume", "persistent volume claim", "storage class"
    ],
    "ações_tecnicas": [
        "deploy", "rollback", "scale up", "scale down", "restart", "reload",
        "refresh", "flush", "clear", "reset", "reset cache", "purge cache",
        "invalidate cache", "warm cache", "preload", "prefetch", "backup",
        "restore", "migrate", "upgrade", "downgrade", "patch", "hotfix",
        "reboot", "shutdown", "start", "stop", "pause", "resume", "suspend",
        "kill", "terminate", "abort", "cancel", "retry", "retry with backoff",
        "circuit break", "timeout", "health check", "liveness probe", "readiness probe",
        "sync", "replicate", "reconcile", "rebalance", "repartition", "reshard",
        "compact", "defragment", "optimize", "analyze", "vacuum", "reindex",
        "rebuild index", "update statistics", "gather statistics", "refresh materialized view"
    ]
}

# Saudações variadas - Português
SAUDACOES_PT = [
    "Oi", "Olá", "Bom dia", "Boa tarde", "Boa noite", "Prezado", "Caro",
    "Prezados", "Caros", "Oi, {nome}", "Olá, {nome}", "E aí, {nome}",
    "Fala, {nome}", "Salve, {nome}", "Oi {nome}", "Olá {nome}"
]

# Saudações variadas - Inglês
SAUDACOES_EN = [
    "Hi", "Hello", "Good morning", "Good afternoon", "Good evening", "Dear", "Hi {name}",
    "Hello {name}", "Hey {name}", "Hey", "Hi there", "Hello there",
    "Good day", "Greetings", "Hi {name}", "Hello {name}"
]

SAUDACOES = SAUDACOES_PT + SAUDACOES_EN

# Transições e conectores variados
TRANSICOES = [
    "Porém", "No entanto", "Mas", "Agora", "Aproveitando", "Já que estamos nisso",
    "Aliás", "A propósito", "Falando nisso", "Já que mencionei", "Enquanto isso",
    "Por outro lado", "Além disso", "Também", "Adicionalmente", "Outra coisa",
    "Só mais uma coisa", "Rapidinho", "Só para constar", "Aproveitando o gancho"
]

# Padrões de ironia/sarcasmo (label 1 - produtivo) - Português
PADROES_IRONIA_PT = [
    "Que surpresa maravilhosa ver que",
    "Adoramos como",
    "É sempre um prazer quando",
    "Que alegria descobrir que",
    "Nada como começar o dia com",
    "Perfeito, mais uma vez",
    "Como sempre, excelente trabalho",
    "Parabéns pelo",
    "Que bom que",
    "Incrível como",
    "Fantástico, o sistema",
    "Maravilhoso, agora",
    "Ótimo, mais uma vez",
    "Excelente, o sistema",
    "Perfeito, o sistema",
    "Que delícia quando",
    "É um prazer imenso quando",
    "Adoramos quando",
    "Que satisfação ver que",
    "É sempre emocionante quando",
    "Que prazer descobrir que",
    "Nada melhor que",
    "É sempre divertido quando",
    "Que alegria ter",
    "É sempre interessante quando",
    "Que sorte nossa que",
    "É sempre reconfortante quando",
    "Que maravilha ver que",
    "É sempre animador quando",
    "Que felicidade descobrir que"
]

# Padrões de ironia/sarcasmo - Inglês
PADROES_IRONIA_EN = [
    "What a wonderful surprise to see that",
    "We love how",
    "It's always a pleasure when",
    "What a joy to discover that",
    "Nothing like starting the day with",
    "Perfect, once again",
    "As always, excellent work",
    "Congratulations on",
    "How great that",
    "Incredible how",
    "Fantastic, the system",
    "Wonderful, now",
    "Great, once again",
    "Excellent, the system",
    "Perfect, the system",
    "What a delight when",
    "It's a great pleasure when",
    "We love when",
    "What satisfaction to see that",
    "It's always exciting when",
    "What a pleasure to discover that",
    "Nothing better than",
    "It's always fun when",
    "What joy to have",
    "It's always interesting when",
    "How lucky we are that",
    "It's always comforting when",
    "What a wonder to see that",
    "It's always encouraging when",
    "What happiness to discover that"
]

PADROES_IRONIA = PADROES_IRONIA_PT + PADROES_IRONIA_EN

# Padrões de agradecimento seguido de solicitação (label 1) - Português
AGRADECIMENTO_SOLICITACAO_PT = [
    ("Muito obrigado", "Aproveitando, você poderia"),
    ("Obrigado", "Aproveitando, pode"),
    ("Agradeço", "Já que estamos nisso, seria possível"),
    ("Valeu", "Aproveitando, você tem como"),
    ("Obrigada", "Aproveitando, você conseguiria"),
    ("Agradecemos", "Já que mencionei, você poderia"),
    ("Parabéns pelo excelente trabalho", "No entanto"),
    ("Parabéns pela dedicação", "Porém"),
    ("Parabéns pelo suporte", "Mas"),
    ("Parabéns pelo profissionalismo", "Agora preciso"),
    ("Parabéns pela rapidez", "Só que agora"),
    ("Parabéns pela qualidade", "Mas agora"),
    ("Parabéns pelo excelente suporte", "No entanto, preciso"),
    ("Parabéns pelo trabalho impecável", "Porém, o"),
    ("Parabéns pela excelência", "Mas agora preciso")
]

# Padrões de agradecimento seguido de solicitação - Inglês
AGRADECIMENTO_SOLICITACAO_EN = [
    ("Thank you very much", "By the way, could you"),
    ("Thanks", "By the way, can you"),
    ("I appreciate", "While we're at it, would it be possible"),
    ("Thanks", "By the way, do you have a way to"),
    ("Thank you", "By the way, could you"),
    ("We appreciate", "Since I mentioned it, could you"),
    ("Congratulations on the excellent work", "However"),
    ("Congratulations on the dedication", "However"),
    ("Congratulations on the support", "But"),
    ("Congratulations on the professionalism", "Now I need"),
    ("Congratulations on the speed", "But now"),
    ("Congratulations on the quality", "But now"),
    ("Congratulations on the excellent support", "However, I need"),
    ("Congratulations on the impeccable work", "However, the"),
    ("Congratulations on the excellence", "But now I need")
]

AGRADECIMENTO_SOLICITACAO = AGRADECIMENTO_SOLICITACAO_PT + AGRADECIMENTO_SOLICITACAO_EN

# Padrões informativos sem ação (label 0) - Português
PADROES_INFORMATIVOS_PT = [
    "Apenas informando que",
    "Só para avisar que",
    "Passando para informar que",
    "Apenas para comunicar que",
    "Só para constar que",
    "Apenas registrando que",
    "Só para deixar registrado que",
    "Apenas para conhecimento que",
    "Só para atualizar que",
    "Apenas para notificar que",
    "Só para comunicar que",
    "Apenas para avisar que"
]

# Padrões informativos sem ação - Inglês
PADROES_INFORMATIVOS_EN = [
    "Just informing that",
    "Just to let you know that",
    "Just passing along that",
    "Just to communicate that",
    "Just for the record",
    "Just registering that",
    "Just to leave it on record that",
    "Just for your information",
    "Just to update that",
    "Just to notify that",
    "Just to communicate that",
    "Just to let you know that"
]

PADROES_INFORMATIVOS = PADROES_INFORMATIVOS_PT + PADROES_INFORMATIVOS_EN

# Padrões de cancelamento/desconsideração (label 0) - Português
PADROES_CANCELAMENTO_PT = [
    "Por favor, desconsidere",
    "Favor ignorar",
    "Por favor, ignore",
    "Favor desconsiderar",
    "Por favor, cancele",
    "Favor cancelar",
    "Por favor, não faça nada",
    "Favor não alterar",
    "Por favor, mantenha como está",
    "Favor manter",
    "Por favor, não toque em nada",
    "Favor não modificar"
]

# Padrões de cancelamento/desconsideração - Inglês
PADROES_CANCELAMENTO_EN = [
    "Please disregard",
    "Please ignore",
    "Please ignore",
    "Please disregard",
    "Please cancel",
    "Please cancel",
    "Please don't do anything",
    "Please don't change",
    "Please keep as is",
    "Please maintain",
    "Please don't touch anything",
    "Please don't modify"
]

PADROES_CANCELAMENTO = PADROES_CANCELAMENTO_PT + PADROES_CANCELAMENTO_EN


def choose_language() -> str:
    """Escolhe aleatoriamente entre português e inglês."""
    return random.choice(["pt", "en"])


def generate_random_person() -> Tuple[str, str, str, str, str]:
    """Gera uma pessoa aleatória."""
    lang = choose_language()
    if lang == "pt":
        nome = random.choice(NOMES_PT)
    else:
        nome = random.choice(NOMES_EN)
    sobrenome = random.choice(SOBRENOMES)
    empresa, dominio = random.choice(CLIENTES)
    email = f"{nome.lower()}.{sobrenome.lower()}@{dominio}"
    return nome, sobrenome, email, empresa


def generate_ironic_productive_email() -> Dict:
    """Gera email produtivo com ironia/sarcasmo."""
    lang = choose_language()
    nome, sobrenome, email, empresa = generate_random_person()
    if lang == "pt":
        destinatario = random.choice(NOMES_PT)
        padrao_ironia = random.choice(PADROES_IRONIA_PT)
        problema = random.choice(TERMOS_TECNICOS["problemas"])
        sistema = random.choice(TERMOS_TECNICOS["sistemas"])
        erro = random.choice(TERMOS_TECNICOS["erros"])
        
        contextos = [
            f"{padrao_ironia} {sistema} {problema} novamente. {random.choice(['Adoramos', 'Apreciamos', 'Valorizamos'])} como a plataforma AutoU nos mantém em alerta constante. Por favor, trate isso com a 'prioridade máxima' de sempre para que possamos, quem sabe, voltar a trabalhar ainda hoje.",
            f"{padrao_ironia} o {sistema} apresentou {erro} em pleno horário de pico. {random.choice(['Que maravilha', 'Que surpresa', 'Que alegria'])}! Por favor, resolva isso {random.choice(['urgentemente', 'com urgência', 'o quanto antes', 'imediatamente'])} para que possamos {random.choice(['retomar a operação', 'voltar ao normal', 'continuar trabalhando', 'operar normalmente'])}.",
            f"{padrao_ironia} {sistema} está {problema} desde {random.choice(['ontem', 'hoje de manhã', 'há algumas horas', 'o início do turno'])}. {random.choice(['Perfeito', 'Excelente', 'Ótimo'])}! Podemos contar com vocês para resolver isso {random.choice(['hoje', 'ainda hoje', 'o quanto antes', 'com urgência'])}?",
            f"{padrao_ironia} {sistema} parou de {random.choice(['funcionar', 'responder', 'processar', 'operar'])}. {random.choice(['Que bom', 'Que ótimo', 'Que maravilha'])}! Precisamos que vocês {random.choice(['verifiquem', 'investiguem', 'corrijam', 'resolvam'])} isso {random.choice(['urgentemente', 'com prioridade', 'o quanto antes'])}.",
        ]
    else:
        destinatario = random.choice(NOMES_EN)
        padrao_ironia = random.choice(PADROES_IRONIA_EN)
        problema = random.choice(TERMOS_TECNICOS["problemas"])
        sistema = random.choice(TERMOS_TECNICOS["sistemas"])
        erro = random.choice(TERMOS_TECNICOS["erros"])
        
        contextos = [
            f"{padrao_ironia} {sistema} {problema} again. {random.choice(['We love', 'We appreciate', 'We value'])} how the AutoU platform keeps us constantly alert. Please treat this with the usual 'maximum priority' so we can, perhaps, get back to work today.",
            f"{padrao_ironia} the {sistema} presented {erro} during peak hours. {random.choice(['What a wonder', 'What a surprise', 'What a joy'])}! Please resolve this {random.choice(['urgently', 'as soon as possible', 'immediately'])} so we can {random.choice(['resume operations', 'get back to normal', 'continue working', 'operate normally'])}.",
            f"{padrao_ironia} {sistema} has been {problema} since {random.choice(['yesterday', 'this morning', 'a few hours ago', 'the start of the shift'])}. {random.choice(['Perfect', 'Excellent', 'Great'])}! Can we count on you to resolve this {random.choice(['today', 'still today', 'as soon as possible', 'urgently'])}?",
            f"{padrao_ironia} {sistema} stopped {random.choice(['working', 'responding', 'processing', 'operating'])}. {random.choice(['How great', 'How wonderful', 'What a wonder'])}! We need you to {random.choice(['check', 'investigate', 'fix', 'resolve'])} this {random.choice(['urgently', 'with priority', 'as soon as possible'])}.",
        ]
    
    texto = random.choice(contextos)
    
    return {
        "text": texto,
        "label": 1
    }


def generate_technical_productive_email() -> Dict:
    """Gera email produtivo com detalhes técnicos específicos."""
    lang = choose_language()
    nome, sobrenome, email, empresa = generate_random_person()
    
    sistema = random.choice(TERMOS_TECNICOS["sistemas"])
    problema = random.choice(TERMOS_TECNICOS["problemas"])
    erro = random.choice(TERMOS_TECNICOS["erros"])
    tecnologia = random.choice(TERMOS_TECNICOS["tecnologias"])
    metrica = random.choice(TERMOS_TECNICOS["métricas"])
    integracao = random.choice(TERMOS_TECNICOS["integrações"])
    
    if lang == "pt":
        destinatario = random.choice(NOMES_PT)
        saudacao = random.choice(SAUDACOES_PT).replace("{nome}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}. O {sistema} está apresentando {problema}. Os logs mostram {erro} constante. Preciso que você verifique se houve alguma alteração na {tecnologia} ou se o servidor de vocês está em manutenção.",
            f"{saudacao}. Notei que o {metrica} do {sistema} subiu de {random.randint(100, 500)}ms para {random.randint(600, 2000)}ms após a última atualização. Isso está começando a gerar gargalo na nossa ponta. Você tem alguma previsão de otimização ou pode checar se há algo errado com o nosso {tecnologia}?",
            f"{saudacao}, {destinatario}. O {sistema} parou de {random.choice(['classificar', 'processar', 'enviar', 'receber', 'sincronizar'])} os {random.choice(['dados', 'registros', 'eventos', 'logs', 'métricas'])} da {random.choice(['unidade', 'fábrica', 'planta', 'filial'])} {random.choice(['Sul', 'Norte', 'Leste', 'Oeste', 'Centro'])}. Os logs mostram {erro}. Preciso que você verifique se houve alguma alteração na {tecnologia} ou se o servidor de vocês está em manutenção.",
            f"{saudacao}. A {integracao} parou de {random.choice(['enviar', 'receber', 'processar', 'sincronizar'])} {random.choice(['notificações', 'dados', 'eventos', 'mensagens', 'logs'])}. Você sabe se houve alguma mudança na política de {random.choice(['tokens', 'autenticação', 'autorização', 'acesso', 'permissões'])}? Precisamos que isso volte a funcionar para o {random.choice(['turno da noite', 'próximo turno', 'fim de semana', 'próxima semana'])}.",
            f"{saudacao}, {destinatario}. O botão de '{random.choice(['Esqueci minha senha', 'Download', 'Exportar', 'Gerar relatório', 'Enviar', 'Confirmar'])}' está direcionando para uma página {erro}. Vários usuários da {empresa} estão reclamando. Pode corrigir esse {random.choice(['redirecionamento', 'endpoint', 'link', 'caminho'])} com urgência?",
            f"{saudacao}. O cliente está na linha e disse que o {random.choice(['email de confirmação', 'webhook', 'callback', 'notificação'])} não está chegando para os domínios {random.choice(TERMOS_TECNICOS['domínios_email'])}. Pode verificar se entramos em alguma {random.choice(['blacklist', 'whitelist', 'spam list', 'block list'])} ou se o serviço de {random.choice(TERMOS_TECNICOS['protocolos'])} está com {random.choice(['fila parada', 'fila travada', 'processamento lento', 'timeout'])}?",
            f"{saudacao}, {destinatario}. Como faço para {random.choice(['extrair', 'gerar', 'exportar', 'obter', 'acessar'])} o {random.choice(['relatório', 'dashboard', 'métrica', 'análise'])} de {random.choice(['produtividade', 'performance', 'qualidade', 'eficiência'])} {random.choice(['mensal', 'semanal', 'diário', 'trimestral'])} segmentado por {random.choice(['setor', 'departamento', 'linha de produção', 'unidade'])}? Procurei em todas as abas e não encontrei essa opção. Se não existir, vocês poderiam gerar isso para mim via {random.choice(['banco de dados', 'API', 'script', 'query SQL'])}?",
            f"{saudacao}. O pessoal aqui da {random.choice(['planta', 'fábrica', 'unidade', 'filial'])} está em dúvida sobre como configurar o {random.choice(['alerta', 'notificação', 'dashboard', 'relatório'])} de {random.choice(['temperatura', 'pressão', 'umidade', 'vazão', 'velocidade'])} no novo {sistema}. O manual não está muito claro nessa parte. Pode nos mandar um {random.choice(['passo a passo', 'tutorial', 'guia', 'documentação'])} ou marcar {random.randint(5, 30)} minutos de call para nos explicar?",
        ]
    else:
        destinatario = random.choice(NOMES_EN)
        saudacao = random.choice(SAUDACOES_EN).replace("{name}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}. The {sistema} is showing {problema}. The logs show constant {erro}. I need you to check if there was any change in {tecnologia} or if your server is under maintenance.",
            f"{saudacao}. I noticed that the {metrica} of {sistema} increased from {random.randint(100, 500)}ms to {random.randint(600, 2000)}ms after the last update. This is starting to create a bottleneck on our end. Do you have any optimization forecast or can you check if something is wrong with our {tecnologia}?",
            f"{saudacao}, {destinatario}. The {sistema} stopped {random.choice(['classifying', 'processing', 'sending', 'receiving', 'synchronizing'])} the {random.choice(['data', 'records', 'events', 'logs', 'metrics'])} from the {random.choice(['unit', 'factory', 'plant', 'branch'])} {random.choice(['South', 'North', 'East', 'West', 'Center'])}. The logs show {erro}. I need you to check if there was any change in {tecnologia} or if your server is under maintenance.",
            f"{saudacao}. The {integracao} stopped {random.choice(['sending', 'receiving', 'processing', 'synchronizing'])} {random.choice(['notifications', 'data', 'events', 'messages', 'logs'])}. Do you know if there was any change in the {random.choice(['tokens', 'authentication', 'authorization', 'access', 'permissions'])} policy? We need this to work again for the {random.choice(['night shift', 'next shift', 'weekend', 'next week'])}.",
            f"{saudacao}, {destinatario}. The '{random.choice(['Forgot password', 'Download', 'Export', 'Generate report', 'Send', 'Confirm'])}' button is redirecting to a {erro} page. Several users from {empresa} are complaining. Can you fix this {random.choice(['redirect', 'endpoint', 'link', 'path'])} urgently?",
            f"{saudacao}. The client is on the line and said that the {random.choice(['confirmation email', 'webhook', 'callback', 'notification'])} is not arriving for domains {random.choice(TERMOS_TECNICOS['domínios_email'])}. Can you check if we entered any {random.choice(['blacklist', 'whitelist', 'spam list', 'block list'])} or if the {random.choice(TERMOS_TECNICOS['protocolos'])} service has {random.choice(['queue stopped', 'queue stuck', 'slow processing', 'timeout'])}?",
            f"{saudacao}, {destinatario}. How do I {random.choice(['extract', 'generate', 'export', 'obtain', 'access'])} the {random.choice(['report', 'dashboard', 'metric', 'analysis'])} of {random.choice(['productivity', 'performance', 'quality', 'efficiency'])} {random.choice(['monthly', 'weekly', 'daily', 'quarterly'])} segmented by {random.choice(['sector', 'department', 'production line', 'unit'])}? I searched all tabs and couldn't find this option. If it doesn't exist, could you generate this for me via {random.choice(['database', 'API', 'script', 'SQL query'])}?",
            f"{saudacao}. The team here at the {random.choice(['plant', 'factory', 'unit', 'branch'])} is unsure about how to configure the {random.choice(['alert', 'notification', 'dashboard', 'report'])} of {random.choice(['temperature', 'pressure', 'humidity', 'flow', 'speed'])} in the new {sistema}. The manual is not very clear on this part. Can you send us a {random.choice(['step by step', 'tutorial', 'guide', 'documentation'])} or schedule {random.randint(5, 30)} minutes of call to explain it to us?",
        ]
    
    texto = random.choice(templates)
    
    return {
        "text": texto,
        "label": 1
    }


def generate_gratitude_with_request_email() -> Dict:
    """Gera email que começa com agradecimento mas tem solicitação (label 1)."""
    lang = choose_language()
    nome, sobrenome, email, empresa = generate_random_person()
    sistema = random.choice(TERMOS_TECNICOS["sistemas"])
    problema = random.choice(TERMOS_TECNICOS["problemas"])
    erro = random.choice(TERMOS_TECNICOS["erros"])
    
    if lang == "pt":
        destinatario = random.choice(NOMES_PT)
        saudacao = random.choice(SAUDACOES_PT).replace("{nome}", destinatario)
        agradecimento, transicao = random.choice(AGRADECIMENTO_SOLICITACAO_PT)
        templates = [
            f"{saudacao}, {destinatario}. {agradecimento} pelo {random.choice(['excelente suporte técnico', 'trabalho realizado', 'suporte prestado', 'rapidez na resolução', 'profissionalismo'])} prestado no {random.choice(['mês passado', 'último mês', 'semana passada', 'última semana'])}. Foi realmente {random.choice(['impecável', 'excelente', 'perfeito', 'excepcional'])}. {transicao} o {random.choice(['faturamento', 'relatório', 'dashboard', 'sistema'])} deste mês veio com o {random.choice(['nome da unidade', 'cabeçalho', 'formato', 'layout'])} errado e o nosso {random.choice(['financeiro', 'contábil', 'jurídico', 'compliance'])} não aceita {random.choice(['a nota', 'o documento', 'o arquivo', 'o relatório'])} assim. Você consegue {random.choice(['corrigir', 'ajustar', 'modificar', 'atualizar'])} e {random.choice(['reenviar', 'enviar novamente', 'reprocessar'])}?",
            f"{saudacao}, {destinatario}. {agradecimento} pelo {random.choice(['envio', 'suporte', 'trabalho', 'ajuda'])}. {transicao} você poderia me enviar o {random.choice(['link', 'arquivo', 'documento', 'acesso'])} da {random.choice(['gravação', 'reunião', 'apresentação', 'documentação'])} da {random.choice(['semana passada', 'última semana', 'reunião anterior'])}? Tentei achar no {random.choice(['portal', 'sistema', 'dashboard', 'painel'])}, mas o botão de {random.choice(['download', 'acesso', 'visualização', 'exportação'])} não faz nada quando clico.",
            f"{saudacao}. {agradecimento} pelo {random.choice(['convite', 'envio', 'informação', 'suporte'])} para o {random.choice(['webinar', 'evento', 'treinamento', 'workshop'])}. {transicao} você poderia me enviar o {random.choice(['link', 'material', 'documentação', 'acesso'])} da {random.choice(['gravação', 'apresentação', 'sessão'])} da {random.choice(['semana passada', 'última semana', 'sessão anterior'])}? Tentei achar no {random.choice(['portal', 'sistema', 'plataforma'])}, mas o botão de {random.choice(['download', 'acesso', 'visualização'])} não funciona.",
            f"{saudacao}, {destinatario}. {agradecimento} pelo {random.choice(['excelente trabalho', 'suporte', 'dedicação', 'profissionalismo'])}. {transicao} o {sistema} está apresentando {problema} e os logs mostram {erro}. Precisamos que vocês {random.choice(['verifiquem', 'investiguem', 'corrijam', 'resolvam'])} isso {random.choice(['urgentemente', 'com prioridade', 'o quanto antes'])}.",
            f"{saudacao}. {agradecimento} pela {random.choice(['atualização', 'correção', 'resolução', 'ajuda'])} anterior. {transicao} agora o {sistema} está {problema} novamente. Os logs indicam {erro}. Podemos contar com vocês para {random.choice(['verificar', 'investigar', 'corrigir', 'resolver'])} isso {random.choice(['hoje', 'ainda hoje', 'o quanto antes'])}?",
        ]
    else:
        destinatario = random.choice(NOMES_EN)
        saudacao = random.choice(SAUDACOES_EN).replace("{name}", destinatario)
        agradecimento, transicao = random.choice(AGRADECIMENTO_SOLICITACAO_EN)
        templates = [
            f"{saudacao}, {destinatario}. {agradecimento} for the {random.choice(['excellent technical support', 'work done', 'support provided', 'quick resolution', 'professionalism'])} provided {random.choice(['last month', 'last month', 'last week', 'last week'])}. It was really {random.choice(['impeccable', 'excellent', 'perfect', 'exceptional'])}. {transicao} the {random.choice(['billing', 'report', 'dashboard', 'system'])} this month came with the wrong {random.choice(['unit name', 'header', 'format', 'layout'])} and our {random.choice(['finance', 'accounting', 'legal', 'compliance'])} doesn't accept {random.choice(['the invoice', 'the document', 'the file', 'the report'])} like that. Can you {random.choice(['fix', 'adjust', 'modify', 'update'])} and {random.choice(['resend', 'send again', 'reprocess'])}?",
            f"{saudacao}, {destinatario}. {agradecimento} for the {random.choice(['sending', 'support', 'work', 'help'])}. {transicao} could you send me the {random.choice(['link', 'file', 'document', 'access'])} of the {random.choice(['recording', 'meeting', 'presentation', 'documentation'])} from {random.choice(['last week', 'last week', 'previous meeting'])}? I tried to find it in the {random.choice(['portal', 'system', 'dashboard', 'panel'])}, but the {random.choice(['download', 'access', 'view', 'export'])} button doesn't do anything when I click.",
            f"{saudacao}. {agradecimento} for the {random.choice(['invitation', 'sending', 'information', 'support'])} for the {random.choice(['webinar', 'event', 'training', 'workshop'])}. {transicao} could you send me the {random.choice(['link', 'material', 'documentation', 'access'])} of the {random.choice(['recording', 'presentation', 'session'])} from {random.choice(['last week', 'last week', 'previous session'])}? I tried to find it in the {random.choice(['portal', 'system', 'platform'])}, but the {random.choice(['download', 'access', 'view'])} button doesn't work.",
            f"{saudacao}, {destinatario}. {agradecimento} for the {random.choice(['excellent work', 'support', 'dedication', 'professionalism'])}. {transicao} the {sistema} is showing {problema} and the logs show {erro}. We need you to {random.choice(['check', 'investigate', 'fix', 'resolve'])} this {random.choice(['urgently', 'with priority', 'as soon as possible'])}.",
            f"{saudacao}. {agradecimento} for the previous {random.choice(['update', 'fix', 'resolution', 'help'])}. {transicao} now the {sistema} is {problema} again. The logs indicate {erro}. Can we count on you to {random.choice(['check', 'investigate', 'fix', 'resolve'])} this {random.choice(['today', 'still today', 'as soon as possible'])}?",
        ]
    
    texto = random.choice(templates)
    
    return {
        "text": texto,
        "label": 1
    }


def generate_technical_unproductive_email() -> Dict:
    """Gera email não produtivo com termos técnicos mas sem ação necessária."""
    lang = choose_language()
    nome, sobrenome, email, empresa = generate_random_person()
    sistema = random.choice(TERMOS_TECNICOS["sistemas"])
    erro = random.choice(TERMOS_TECNICOS["erros"])
    tecnologia = random.choice(TERMOS_TECNICOS["tecnologias"])
    
    if lang == "pt":
        destinatario = random.choice(NOMES_PT)
        saudacao = random.choice(SAUDACOES_PT).replace("{nome}", destinatario)
        padrao_informativo = random.choice(PADROES_INFORMATIVOS_PT)
        templates = [
            f"{saudacao}, {destinatario}. {padrao_informativo} o {erro} que reportamos anteriormente na {random.choice(['integração', 'sincronização', 'conexão'])} com a {empresa} parou de ocorrer subitamente. Fizemos um {random.choice(['trace', 'debug', 'log analysis', 'diagnóstico'])} e parece que o {random.choice(['servidor', 'sistema', 'serviço'])} estabilizou sozinho. Não toque em nada e não altere as {random.choice(['configurações', 'parâmetros', 'settings'])} atuais, pois o sistema está em {random.choice(['produção', 'operação', 'uso ativo'])} e não queremos novos riscos agora. Apenas registre que o caso está encerrado.",
            f"{saudacao}! Verificamos que houve uma tentativa de {random.choice(['acesso não autorizado', 'login suspeito', 'conexão inválida'])} na nossa conta. O {sistema} de {random.choice(['segurança', 'proteção', 'monitoramento'])} de vocês bloqueou a ação instantaneamente, o que foi {random.choice(['ótimo', 'excelente', 'perfeito'])}. Como o bloqueio foi {random.choice(['automático', 'imediato', 'instantâneo'])} e o {random.choice(['invasor', 'usuário', 'atacante'])} não conseguiu entrar, não precisamos de nenhuma {random.choice(['medida adicional', 'ação', 'intervenção'])} de vocês por enquanto. {random.choice(['Bom trabalho', 'Parabéns', 'Excelente'])}.",
            f"{saudacao}. {padrao_informativo} a {random.choice(['manutenção', 'atualização', 'migração'])} dos {random.choice(['bancos de dados', 'servidores', 'sistemas'])} da {empresa} foi concluída com sucesso. Houve um pequeno atraso de {random.randint(5, 30)} minutos, mas nada que impactasse a {random.choice(['API', 'integração', 'sistema'])} de vocês. Não há necessidade de {random.choice(['suporte', 'verificação', 'intervenção', 'ação'])} ou {random.choice(['verificação de logs', 'análise', 'investigação'])}.",
            f"{saudacao}. Recebemos o aviso de que a {random.choice(['versão', 'release', 'build'])} {random.choice(['2.4', '3.0', '1.8', '4.2'])} será {random.choice(['descontinuada', 'depreciada', 'removida'])}. Já migramos todos os nossos {random.choice(['endpoints', 'integrações', 'sistemas'])} para a {random.choice(['3.0', '4.0', '2.0'])} e os testes foram {random.choice(['positivos', 'bem-sucedidos', 'aprovados'])}. Não temos dúvidas nem precisamos de {random.choice(['auxílio', 'suporte', 'ajuda'])} na migração. Obrigado pelo aviso antecipado.",
            f"{saudacao}, {destinatario}. {padrao_informativo} nosso {random.choice(['escritório', 'fábrica', 'unidade'])} estará {random.choice(['fechado', 'sem operação', 'sem pessoal'])} devido ao {random.choice(['feriado local', 'manutenção programada', 'evento corporativo'])} {random.choice(['amanhã', 'na próxima semana', 'no próximo mês'])}. Não haverá ninguém para {random.choice(['operar', 'monitorar', 'gerenciar'])} o {sistema} AutoU, portanto, qualquer {erro} que ocorrer não será {random.choice(['visualizado', 'monitorado', 'detectado'])} por nós até {random.choice(['segunda-feira', 'o retorno', 'a próxima semana'])}. Não é necessário {random.choice(['suporte', 'intervenção', 'ação'])} durante o período.",
            f"{saudacao}, {destinatario}. {padrao_informativo} o {random.choice(['bug', 'erro', 'problema'])} que eu mencionei no {random.choice(['café', 'almoço', 'encontro', 'evento'])} {random.choice(['ontem', 'na semana passada', 'no mês passado'])} era, na verdade, um {random.choice(['erro de digitação', 'mal-entendido', 'configuração incorreta'])} do nosso {random.choice(['estagiário', 'colaborador', 'usuário'])}. O {random.choice(['código', 'sistema', 'serviço'])} de vocês está {random.choice(['perfeito', 'correto', 'funcionando bem'])}. Desculpe a confusão e ignore o meu comentário anterior sobre {random.choice(['lentidão', 'erro', 'problema', 'falha'])}.",
            f"{saudacao}, {destinatario}. {padrao_informativo} a {random.choice(['solicitação', 'requisição', 'demanda'])} de {random.choice(['troca de servidor', 'migração', 'atualização', 'expansão'])} que havíamos {random.choice(['planejado', 'solicitado', 'discutido'])} foi {random.choice(['cancelada', 'suspensa', 'adiada'])} pela nossa {random.choice(['diretoria', 'gerência', 'liderança'])}. Por favor, desconsidere o {random.choice(['e-mail', 'pedido', 'solicitação'])} anterior e mantenha tudo como está. Não faremos a {random.choice(['migração', 'atualização', 'mudança'])} este {random.choice(['mês', 'trimestre', 'semestre'])}.",
            f"{saudacao}, {destinatario}. {random.choice(['Agradeço', 'Agradecemos', 'Muito obrigado', 'Muito obrigada'])} pelo {random.choice(['envio', 'suporte', 'trabalho'])} das {random.choice(['credenciais', 'configurações', 'documentação'])}. Já conseguimos {random.choice(['acessar', 'configurar', 'implementar'])} e já {random.choice(['configuramos', 'implementamos', 'testamos'])} tudo. Funcionou {random.choice(['perfeitamente', 'sem problemas', 'corretamente'])} de primeira. Não temos mais nenhuma {random.choice(['pendência', 'dúvida', 'questão'])}. Um abraço.",
        ]
    else:
        destinatario = random.choice(NOMES_EN)
        saudacao = random.choice(SAUDACOES_EN).replace("{name}", destinatario)
        padrao_informativo = random.choice(PADROES_INFORMATIVOS_EN)
        templates = [
            f"{saudacao}, {destinatario}. {padrao_informativo} the {erro} we reported earlier in the {random.choice(['integration', 'synchronization', 'connection'])} with {empresa} stopped occurring suddenly. We did a {random.choice(['trace', 'debug', 'log analysis', 'diagnosis'])} and it seems the {random.choice(['server', 'system', 'service'])} stabilized on its own. Don't touch anything and don't change the current {random.choice(['settings', 'parameters', 'settings'])}, as the system is in {random.choice(['production', 'operation', 'active use'])} and we don't want new risks now. Just record that the case is closed.",
            f"{saudacao}! We verified that there was an attempt of {random.choice(['unauthorized access', 'suspicious login', 'invalid connection'])} on our account. Your {sistema} of {random.choice(['security', 'protection', 'monitoring'])} blocked the action instantly, which was {random.choice(['great', 'excellent', 'perfect'])}. Since the block was {random.choice(['automatic', 'immediate', 'instant'])} and the {random.choice(['intruder', 'user', 'attacker'])} couldn't get in, we don't need any {random.choice(['additional measures', 'action', 'intervention'])} from you for now. {random.choice(['Good work', 'Congratulations', 'Excellent'])}.",
            f"{saudacao}. {padrao_informativo} the {random.choice(['maintenance', 'update', 'migration'])} of the {random.choice(['databases', 'servers', 'systems'])} of {empresa} was completed successfully. There was a small delay of {random.randint(5, 30)} minutes, but nothing that impacted your {random.choice(['API', 'integration', 'system'])}. There is no need for {random.choice(['support', 'verification', 'intervention', 'action'])} or {random.choice(['log verification', 'analysis', 'investigation'])}.",
            f"{saudacao}. We received the notice that version {random.choice(['2.4', '3.0', '1.8', '4.2'])} will be {random.choice(['discontinued', 'deprecated', 'removed'])}. We've already migrated all our {random.choice(['endpoints', 'integrations', 'systems'])} to {random.choice(['3.0', '4.0', '2.0'])} and the tests were {random.choice(['positive', 'successful', 'approved'])}. We have no doubts and don't need any {random.choice(['assistance', 'support', 'help'])} with the migration. Thanks for the advance notice.",
            f"{saudacao}, {destinatario}. {padrao_informativo} our {random.choice(['office', 'factory', 'unit'])} will be {random.choice(['closed', 'without operation', 'without staff'])} due to {random.choice(['local holiday', 'scheduled maintenance', 'corporate event'])} {random.choice(['tomorrow', 'next week', 'next month'])}. There will be no one to {random.choice(['operate', 'monitor', 'manage'])} the AutoU {sistema}, therefore, any {erro} that occurs will not be {random.choice(['viewed', 'monitored', 'detected'])} by us until {random.choice(['Monday', 'the return', 'next week'])}. No {random.choice(['support', 'intervention', 'action'])} is needed during the period.",
            f"{saudacao}, {destinatario}. {padrao_informativo} the {random.choice(['bug', 'error', 'problem'])} I mentioned at the {random.choice(['coffee', 'lunch', 'meeting', 'event'])} {random.choice(['yesterday', 'last week', 'last month'])} was actually a {random.choice(['typo', 'misunderstanding', 'incorrect configuration'])} from our {random.choice(['intern', 'collaborator', 'user'])}. Your {random.choice(['code', 'system', 'service'])} is {random.choice(['perfect', 'correct', 'working well'])}. Sorry for the confusion and ignore my previous comment about {random.choice(['slowness', 'error', 'problem', 'failure'])}.",
            f"{saudacao}, {destinatario}. {padrao_informativo} the {random.choice(['request', 'requisition', 'demand'])} for {random.choice(['server change', 'migration', 'update', 'expansion'])} that we had {random.choice(['planned', 'requested', 'discussed'])} was {random.choice(['canceled', 'suspended', 'postponed'])} by our {random.choice(['board', 'management', 'leadership'])}. Please disregard the previous {random.choice(['email', 'request', 'solicitation'])} and keep everything as is. We won't do the {random.choice(['migration', 'update', 'change'])} this {random.choice(['month', 'quarter', 'semester'])}.",
            f"{saudacao}, {destinatario}. {random.choice(['I appreciate', 'We appreciate', 'Thank you very much', 'Thank you very much'])} for the {random.choice(['sending', 'support', 'work'])} of the {random.choice(['credentials', 'settings', 'documentation'])}. We already managed to {random.choice(['access', 'configure', 'implement'])} and we already {random.choice(['configured', 'implemented', 'tested'])} everything. It worked {random.choice(['perfectly', 'without problems', 'correctly'])} from the start. We have no more {random.choice(['pending', 'doubt', 'question'])}. Best regards.",
        ]
    
    texto = random.choice(templates)
    
    return {
        "text": texto,
        "label": 0
    }


def generate_gratitude_unproductive_email() -> Dict:
    """Gera email não produtivo apenas com agradecimento/elogio."""
    lang = choose_language()
    nome, sobrenome, email, empresa = generate_random_person()
    sistema = random.choice(TERMOS_TECNICOS["sistemas"])
    
    if lang == "pt":
        destinatario = random.choice(NOMES_PT)
        saudacao = random.choice(SAUDACOES_PT).replace("{nome}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}. {random.choice(['Que prazer', 'É um prazer', 'Foi um prazer'])} falar com você. O {sistema} está simplesmente {random.choice(['incrível', 'fantástico', 'excepcional'])}, a {random.choice(['interface nova', 'atualização', 'versão nova'])} mudou nossa {random.choice(['produtividade', 'eficiência', 'performance'])}. Só passando para deixar esse {random.choice(['feedback positivo', 'reconhecimento', 'elogio'])}. Sem {random.choice(['bugs', 'erros', 'problemas'])}, sem {random.choice(['reclamações', 'pendências', 'questões'])}, apenas {random.choice(['elogios', 'reconhecimento', 'parabéns'])} da equipe de {random.choice(['TI', 'tecnologia', 'sistemas'])} da {empresa}.",
            f"{saudacao}. A equipe da {empresa} gostaria de {random.choice(['parabenizar', 'congratular', 'reconhecer'])} a AutoU pelo {random.choice(['prêmio de inovação', 'excelente trabalho', 'sucesso do projeto', 'qualidade do serviço'])}. Ficamos muito {random.choice(['felizes', 'orgulhosos', 'satisfeitos'])} em ser {random.choice(['parceiros', 'clientes', 'colaboradores'])} de uma empresa tão {random.choice(['competente', 'profissional', 'dedicada'])}. {random.choice(['Celebrem muito', 'Parabéns', 'Muito sucesso'])} com a equipe!",
            f"{saudacao}, {destinatario}. {random.choice(['Parabéns', 'Parabéns pelo', 'Parabéns pela'])} {random.choice(['excelente trabalho', 'dedicação', 'profissionalismo', 'qualidade'])} prestado no {random.choice(['mês passado', 'último mês', 'projeto', 'sistema'])}. Foi realmente {random.choice(['impecável', 'excepcional', 'perfeito'])}. O {sistema} está {random.choice(['funcionando perfeitamente', 'operando sem problemas', 'estável e confiável'])} e não temos {random.choice(['nenhuma pendência', 'nenhuma questão', 'nenhum problema'])} no momento.",
            f"{saudacao}. {random.choice(['Agradeço', 'Agradecemos', 'Muito obrigado', 'Muito obrigada'])} pelo {random.choice(['excelente suporte', 'trabalho realizado', 'dedicação', 'profissionalismo'])}. O {sistema} está {random.choice(['funcionando muito bem', 'operando perfeitamente', 'estável'])} e não há necessidade de nenhuma {random.choice(['ação', 'intervenção', 'alteração'])} adicional. {random.choice(['Continuaremos', 'Seguiremos'])} utilizando o sistema normalmente.",
        ]
    else:
        destinatario = random.choice(NOMES_EN)
        saudacao = random.choice(SAUDACOES_EN).replace("{name}", destinatario)
        pleasure_phrases = ['What a pleasure', "It's a pleasure", 'It was a pleasure']
        templates = [
            f"{saudacao}, {destinatario}. {random.choice(pleasure_phrases)} talking to you. The {sistema} is simply {random.choice(['incredible', 'fantastic', 'exceptional'])}, the {random.choice(['new interface', 'update', 'new version'])} changed our {random.choice(['productivity', 'efficiency', 'performance'])}. Just passing by to leave this {random.choice(['positive feedback', 'recognition', 'praise'])}. No {random.choice(['bugs', 'errors', 'problems'])}, no {random.choice(['complaints', 'pending', 'issues'])}, just {random.choice(['praise', 'recognition', 'congratulations'])} from the {random.choice(['IT', 'technology', 'systems'])} team of {empresa}.",
            f"{saudacao}. The {empresa} team would like to {random.choice(['congratulate', 'congratulate', 'recognize'])} AutoU for the {random.choice(['innovation award', 'excellent work', 'project success', 'service quality'])}. We are very {random.choice(['happy', 'proud', 'satisfied'])} to be {random.choice(['partners', 'clients', 'collaborators'])} of such a {random.choice(['competent', 'professional', 'dedicated'])} company. {random.choice(['Celebrate a lot', 'Congratulations', 'Much success'])} with the team!",
            f"{saudacao}, {destinatario}. {random.choice(['Congratulations', 'Congratulations on', 'Congratulations on the'])} {random.choice(['excellent work', 'dedication', 'professionalism', 'quality'])} provided {random.choice(['last month', 'last month', 'project', 'system'])}. It was really {random.choice(['impeccable', 'exceptional', 'perfect'])}. The {sistema} is {random.choice(['working perfectly', 'operating without problems', 'stable and reliable'])} and we have {random.choice(['no pending', 'no issues', 'no problems'])} at the moment.",
            f"{saudacao}. {random.choice(['I appreciate', 'We appreciate', 'Thank you very much', 'Thank you very much'])} for the {random.choice(['excellent support', 'work done', 'dedication', 'professionalism'])}. The {sistema} is {random.choice(['working very well', 'operating perfectly', 'stable'])} and there is no need for any additional {random.choice(['action', 'intervention', 'change'])}. {random.choice(['We will continue', 'We will follow'])} using the system normally.",
        ]
    
    texto = random.choice(templates)
    
    return {
        "text": texto,
        "label": 0
    }


def generate_confusing_productive_email() -> Dict:
    """Gera email produtivo confuso com múltiplas solicitações misturadas."""
    lang = choose_language()
    nome, sobrenome, email, empresa = generate_random_person()
    sistema1 = random.choice(TERMOS_TECNICOS["sistemas"])
    sistema2 = random.choice(TERMOS_TECNICOS["sistemas"])
    problema1 = random.choice(TERMOS_TECNICOS["problemas"])
    problema2 = random.choice(TERMOS_TECNICOS["problemas"])
    erro = random.choice(TERMOS_TECNICOS["erros"])
    
    if lang == "pt":
        destinatario = random.choice(NOMES_PT)
        saudacao = random.choice(SAUDACOES_PT).replace("{nome}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}. O {sistema1} está {problema1} e também o {sistema2} está com {problema2}. Não sei se são problemas relacionados ou não, mas precisamos resolver ambos. Além disso, os logs mostram {erro} no {sistema1}, mas não tenho certeza se isso é a causa ou consequência. Você pode {random.choice(['verificar', 'investigar', 'analisar'])} e me dizer o que fazer?",
            f"{saudacao}. Tivemos {problema1} no {sistema1} ontem, mas hoje está funcionando. Porém, agora o {sistema2} está {problema2} e não sei se tem a ver. Os logs mostram {erro} mas não consigo entender o contexto. Preciso de ajuda para {random.choice(['entender', 'resolver', 'diagnosticar'])} isso.",
            f"{saudacao}, {destinatario}. O {sistema1} parou de funcionar, mas não sei se foi por causa do {sistema2} ou se foi o contrário. Os dois estão {random.choice(['com problemas', 'fora do ar', 'lentos'])} agora. Além disso, preciso {random.choice(['atualizar', 'configurar', 'ajustar'])} algo mas não sei o quê. Você pode me ajudar?",
            f"{saudacao}. Estou com dúvidas sobre o {sistema1}. Ele está {problema1} mas também preciso {random.choice(['configurar', 'ajustar', 'atualizar'])} o {sistema2} que está {problema2}. Não sei por onde começar. Os logs mostram {erro} mas não entendo o que significa. Pode me orientar?",
            f"{saudacao}, {destinatario}. O {sistema1} está {problema1} desde {random.choice(['ontem', 'hoje de manhã', 'há algumas horas'])}. Tentei {random.choice(['reiniciar', 'recarregar', 'atualizar'])} mas não funcionou. Agora o {sistema2} também está {problema2}. Não sei se são coisas relacionadas ou não. Preciso de suporte para {random.choice(['entender', 'resolver', 'corrigir'])} isso.",
        ]
    else:
        destinatario = random.choice(NOMES_EN)
        saudacao = random.choice(SAUDACOES_EN).replace("{name}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}. The {sistema1} is {problema1} and also the {sistema2} has {problema2}. I don't know if they're related problems or not, but we need to resolve both. Also, the logs show {erro} in {sistema1}, but I'm not sure if that's the cause or consequence. Can you {random.choice(['check', 'investigate', 'analyze'])} and tell me what to do?",
            f"{saudacao}. We had {problema1} in {sistema1} yesterday, but today it's working. However, now {sistema2} is {problema2} and I don't know if it's related. The logs show {erro} but I can't understand the context. I need help to {random.choice(['understand', 'resolve', 'diagnose'])} this.",
            f"{saudacao}, {destinatario}. The {sistema1} stopped working, but I don't know if it was because of {sistema2} or the other way around. Both are {random.choice(['with problems', 'down', 'slow'])} now. Also, I need to {random.choice(['update', 'configure', 'adjust'])} something but I don't know what. Can you help me?",
            f"{saudacao}. I have doubts about {sistema1}. It's {problema1} but I also need to {random.choice(['configure', 'adjust', 'update'])} {sistema2} which is {problema2}. I don't know where to start. The logs show {erro} but I don't understand what it means. Can you guide me?",
            f"{saudacao}, {destinatario}. The {sistema1} has been {problema1} since {random.choice(['yesterday', 'this morning', 'a few hours ago'])}. I tried {random.choice(['restarting', 'reloading', 'updating'])} but it didn't work. Now {sistema2} is also {problema2}. I don't know if they're related or not. I need support to {random.choice(['understand', 'resolve', 'fix'])} this.",
        ]
    
    texto = random.choice(templates)
    
    return {
        "text": texto,
        "label": 1
    }


def generate_ambiguous_productive_email() -> Dict:
    """Gera email produtivo ambíguo que pode parecer não produtivo."""
    lang = choose_language()
    nome, sobrenome, email, empresa = generate_random_person()
    sistema = random.choice(TERMOS_TECNICOS["sistemas"])
    problema = random.choice(TERMOS_TECNICOS["problemas"])
    
    if lang == "pt":
        destinatario = random.choice(NOMES_PT)
        saudacao = random.choice(SAUDACOES_PT).replace("{nome}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}. O {sistema} está {problema} mas não é urgente. Só queria saber se vocês podem {random.choice(['verificar', 'dar uma olhada', 'checar'])} quando tiverem um tempinho. Não precisa ser agora, mas seria bom resolver isso {random.choice(['esta semana', 'nos próximos dias', 'quando possível'])}.",
            f"{saudacao}. Notei que o {sistema} está {problema}. Não está {random.choice(['crítico', 'urgente', 'bloqueando'])} ainda, mas seria bom {random.choice(['verificar', 'investigar', 'corrigir'])} antes que vire um problema maior. Quando vocês tiverem disponibilidade, podem {random.choice(['dar uma olhada', 'verificar', 'checar'])}?",
            f"{saudacao}, {destinatario}. O {sistema} está {problema} mas ainda está {random.choice(['funcionando', 'operacional', 'respondendo'])}. Só queria {random.choice(['avisar', 'informar', 'comunicar'])} para vocês {random.choice(['ficarem cientes', 'saberem', 'ficarem informados'])}. Se puderem {random.choice(['verificar', 'investigar', 'analisar'])} quando tiverem tempo, seria ótimo.",
            f"{saudacao}. O {sistema} está {problema} mas não está {random.choice(['impactando', 'afetando', 'bloqueando'])} a operação ainda. Só queria {random.choice(['comunicar', 'informar', 'avisar'])} para vocês {random.choice(['saberem', 'ficarem cientes', 'ficarem informados'])}. Se puderem {random.choice(['dar uma olhada', 'verificar', 'checar'])} quando possível, agradeço.",
            f"{saudacao}, {destinatario}. Notei que o {sistema} está {problema}. Não é {random.choice(['urgente', 'crítico', 'prioritário'])} no momento, mas seria interessante {random.choice(['verificar', 'investigar', 'analisar'])} para evitar problemas futuros. Quando vocês tiverem disponibilidade, podem {random.choice(['dar uma olhada', 'verificar', 'checar'])}?",
        ]
    else:
        destinatario = random.choice(NOMES_EN)
        saudacao = random.choice(SAUDACOES_EN).replace("{name}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}. The {sistema} is {problema} but it's not urgent. I just wanted to know if you can {random.choice(['check', 'take a look', 'verify'])} when you have a moment. It doesn't need to be now, but it would be good to resolve this {random.choice(['this week', 'in the next few days', 'when possible'])}.",
            f"{saudacao}. I noticed that {sistema} is {problema}. It's not {random.choice(['critical', 'urgent', 'blocking'])} yet, but it would be good to {random.choice(['check', 'investigate', 'fix'])} before it becomes a bigger problem. When you have availability, can you {random.choice(['take a look', 'check', 'verify'])}?",
            f"{saudacao}, {destinatario}. The {sistema} is {problema} but it's still {random.choice(['working', 'operational', 'responding'])}. I just wanted to {random.choice(['let you know', 'inform', 'communicate'])} so you {random.choice(['are aware', 'know', 'are informed'])}. If you can {random.choice(['check', 'investigate', 'analyze'])} when you have time, that would be great.",
            f"{saudacao}. The {sistema} is {problema} but it's not {random.choice(['impacting', 'affecting', 'blocking'])} the operation yet. I just wanted to {random.choice(['communicate', 'inform', 'let you know'])} so you {random.choice(['know', 'are aware', 'are informed'])}. If you can {random.choice(['take a look', 'check', 'verify'])} when possible, I appreciate it.",
            f"{saudacao}, {destinatario}. I noticed that {sistema} is {problema}. It's not {random.choice(['urgent', 'critical', 'priority'])} at the moment, but it would be interesting to {random.choice(['check', 'investigate', 'analyze'])} to avoid future problems. When you have availability, can you {random.choice(['take a look', 'check', 'verify'])}?",
        ]
    
    texto = random.choice(templates)
    
    return {
        "text": texto,
        "label": 1
    }


def generate_mixed_context_email() -> Dict:
    """Gera email produtivo com contexto misturado (agradecimento + problema + solicitação)."""
    lang = choose_language()
    nome, sobrenome, email, empresa = generate_random_person()
    sistema = random.choice(TERMOS_TECNICOS["sistemas"])
    problema = random.choice(TERMOS_TECNICOS["problemas"])
    erro = random.choice(TERMOS_TECNICOS["erros"])
    
    if lang == "pt":
        destinatario = random.choice(NOMES_PT)
        saudacao = random.choice(SAUDACOES_PT).replace("{nome}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}. {random.choice(['Obrigado', 'Agradeço', 'Valeu'])} pelo {random.choice(['suporte', 'trabalho', 'ajuda'])} anterior. O {sistema} estava funcionando bem, mas agora está {problema} novamente. Os logs mostram {erro}. Não sei se tem a ver com a {random.choice(['última atualização', 'última mudança', 'última configuração'])} que vocês fizeram. Pode {random.choice(['verificar', 'investigar', 'checar'])}?",
            f"{saudacao}. {random.choice(['Parabéns', 'Parabéns pelo', 'Parabéns pela'])} {random.choice(['excelente trabalho', 'dedicação', 'profissionalismo'])}. O {sistema} estava {random.choice(['perfeito', 'funcionando bem', 'estável'])} até {random.choice(['ontem', 'hoje de manhã', 'há algumas horas'])}. Agora está {problema} e os logs indicam {erro}. Seria possível {random.choice(['verificar', 'investigar', 'corrigir'])} isso?",
            f"{saudacao}, {destinatario}. {random.choice(['Muito obrigado', 'Obrigado', 'Agradeço'])} pela {random.choice(['atualização', 'correção', 'resolução'])} anterior. Funcionou {random.choice(['perfeitamente', 'muito bem', 'bem'])} por um tempo, mas agora o {sistema} está {problema} novamente. Os logs mostram {erro}. Não sei se é {random.choice(['relacionado', 'consequência', 'causado'])} pela {random.choice(['última mudança', 'última atualização', 'última configuração'])}. Pode {random.choice(['verificar', 'investigar', 'analisar'])}?",
            f"{saudacao}. O {sistema} estava {random.choice(['funcionando perfeitamente', 'estável', 'operacional'])} e {random.choice(['agradeço', 'parabenizo', 'reconheço'])} o trabalho de vocês. Porém, desde {random.choice(['ontem', 'hoje de manhã', 'há algumas horas'])} está {problema}. Os logs mostram {erro}. Seria possível {random.choice(['verificar', 'investigar', 'corrigir'])} quando tiverem disponibilidade?",
        ]
    else:
        destinatario = random.choice(NOMES_EN)
        saudacao = random.choice(SAUDACOES_EN).replace("{name}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}. {random.choice(['Thanks', 'I appreciate', 'Thanks'])} for the previous {random.choice(['support', 'work', 'help'])}. The {sistema} was working well, but now it's {problema} again. The logs show {erro}. I don't know if it has to do with the {random.choice(['last update', 'last change', 'last configuration'])} you made. Can you {random.choice(['check', 'investigate', 'verify'])}?",
            f"{saudacao}. {random.choice(['Congratulations', 'Congratulations on', 'Congratulations on the'])} {random.choice(['excellent work', 'dedication', 'professionalism'])}. The {sistema} was {random.choice(['perfect', 'working well', 'stable'])} until {random.choice(['yesterday', 'this morning', 'a few hours ago'])}. Now it's {problema} and the logs indicate {erro}. Would it be possible to {random.choice(['check', 'investigate', 'fix'])} this?",
            f"{saudacao}, {destinatario}. {random.choice(['Thank you very much', 'Thanks', 'I appreciate'])} for the previous {random.choice(['update', 'fix', 'resolution'])}. It worked {random.choice(['perfectly', 'very well', 'well'])} for a while, but now the {sistema} is {problema} again. The logs show {erro}. I don't know if it's {random.choice(['related', 'consequence', 'caused'])} by the {random.choice(['last change', 'last update', 'last configuration'])}. Can you {random.choice(['check', 'investigate', 'analyze'])}?",
            f"{saudacao}. The {sistema} was {random.choice(['working perfectly', 'stable', 'operational'])} and I {random.choice(['appreciate', 'congratulate', 'recognize'])} your work. However, since {random.choice(['yesterday', 'this morning', 'a few hours ago'])} it's been {problema}. The logs show {erro}. Would it be possible to {random.choice(['check', 'investigate', 'fix'])} when you have availability?",
        ]
    
    texto = random.choice(templates)
    
    return {
        "text": texto,
        "label": 1
    }


def generate_technical_but_unproductive_email() -> Dict:
    """Gera email não produtivo com muitos termos técnicos mas sem ação necessária."""
    lang = choose_language()
    nome, sobrenome, email, empresa = generate_random_person()
    sistema = random.choice(TERMOS_TECNICOS["sistemas"])
    tecnologia = random.choice(TERMOS_TECNICOS["tecnologias"])
    metrica = random.choice(TERMOS_TECNICOS["métricas"])
    ambiente = random.choice(TERMOS_TECNICOS["ambientes"])
    
    if lang == "pt":
        destinatario = random.choice(NOMES_PT)
        saudacao = random.choice(SAUDACOES_PT).replace("{nome}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}. Apenas para {random.choice(['informar', 'comunicar', 'atualizar'])} que o {sistema} no {ambiente} está {random.choice(['funcionando perfeitamente', 'operando normalmente', 'estável'])}. As {metrica} estão {random.choice(['dentro do esperado', 'normais', 'estáveis'])} e não há necessidade de {random.choice(['intervenção', 'ação', 'ajuste'])}. O {tecnologia} está {random.choice(['operacional', 'funcionando', 'estável'])} e tudo está {random.choice(['correto', 'ok', 'normal'])}.",
            f"{saudacao}. Só para {random.choice(['comunicar', 'informar', 'atualizar'])} que fizemos uma {random.choice(['análise', 'verificação', 'auditoria'])} do {sistema} e tudo está {random.choice(['funcionando corretamente', 'operacional', 'estável'])}. As {metrica} estão {random.choice(['dentro dos parâmetros', 'normais', 'esperadas'])} e o {tecnologia} no {ambiente} está {random.choice(['operando normalmente', 'funcionando bem', 'estável'])}. Não há necessidade de nenhuma {random.choice(['ação', 'intervenção', 'alteração'])}.",
            f"{saudacao}, {destinatario}. Apenas para {random.choice(['informar', 'comunicar', 'registrar'])} que o {sistema} no {ambiente} está {random.choice(['operando normalmente', 'funcionando perfeitamente', 'estável'])}. O {tecnologia} está {random.choice(['configurado corretamente', 'funcionando bem', 'operacional'])} e as {metrica} estão {random.choice(['dentro do esperado', 'normais', 'estáveis'])}. Não precisamos de nenhuma {random.choice(['intervenção', 'ação', 'ajuste'])} no momento.",
            f"{saudacao}. Só para {random.choice(['comunicar', 'informar', 'atualizar'])} que verificamos o {sistema} e tudo está {random.choice(['funcionando corretamente', 'operacional', 'estável'])}. O {tecnologia} no {ambiente} está {random.choice(['operando normalmente', 'funcionando bem', 'estável'])} e as {metrica} estão {random.choice(['dentro dos parâmetros', 'normais', 'esperadas'])}. Não há necessidade de {random.choice(['suporte', 'intervenção', 'ação'])}.",
        ]
    else:
        destinatario = random.choice(NOMES_EN)
        saudacao = random.choice(SAUDACOES_EN).replace("{name}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}. Just to {random.choice(['inform', 'communicate', 'update'])} that the {sistema} in {ambiente} is {random.choice(['working perfectly', 'operating normally', 'stable'])}. The {metrica} are {random.choice(['within expected', 'normal', 'stable'])} and there is no need for {random.choice(['intervention', 'action', 'adjustment'])}. The {tecnologia} is {random.choice(['operational', 'working', 'stable'])} and everything is {random.choice(['correct', 'ok', 'normal'])}.",
            f"{saudacao}. Just to {random.choice(['communicate', 'inform', 'update'])} that we did an {random.choice(['analysis', 'verification', 'audit'])} of {sistema} and everything is {random.choice(['working correctly', 'operational', 'stable'])}. The {metrica} are {random.choice(['within parameters', 'normal', 'expected'])} and the {tecnologia} in {ambiente} is {random.choice(['operating normally', 'working well', 'stable'])}. There is no need for any {random.choice(['action', 'intervention', 'change'])}.",
            f"{saudacao}, {destinatario}. Just to {random.choice(['inform', 'communicate', 'record'])} that the {sistema} in {ambiente} is {random.choice(['operating normally', 'working perfectly', 'stable'])}. The {tecnologia} is {random.choice(['configured correctly', 'working well', 'operational'])} and the {metrica} are {random.choice(['within expected', 'normal', 'stable'])}. We don't need any {random.choice(['intervention', 'action', 'adjustment'])} at the moment.",
            f"{saudacao}. Just to {random.choice(['communicate', 'inform', 'update'])} that we checked {sistema} and everything is {random.choice(['working correctly', 'operational', 'stable'])}. The {tecnologia} in {ambiente} is {random.choice(['operating normally', 'working well', 'stable'])} and the {metrica} are {random.choice(['within parameters', 'normal', 'expected'])}. There is no need for {random.choice(['support', 'intervention', 'action'])}.",
        ]
    
    texto = random.choice(templates)
    
    return {
        "text": texto,
        "label": 0
    }


def generate_negation_complex_email() -> Dict:
    """Gera email não produtivo com negações complexas de ações."""
    lang = choose_language()
    nome, sobrenome, email, empresa = generate_random_person()
    sistema = random.choice(TERMOS_TECNICOS["sistemas"])
    problema = random.choice(TERMOS_TECNICOS["problemas"])
    erro = random.choice(TERMOS_TECNICOS["erros"])
    acao = random.choice(TERMOS_TECNICOS["ações_tecnicas"])
    
    if lang == "pt":
        destinatario = random.choice(NOMES_PT)
        saudacao = random.choice(SAUDACOES_PT).replace("{nome}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}. O {sistema} estava {problema} mas {random.choice(['já não está mais', 'não está mais', 'parou de estar'])}. Fizemos um {random.choice(['trace', 'debug', 'análise'])} e parece que {random.choice(['resolveu sozinho', 'estabilizou', 'normalizou'])}. Não precisamos que vocês {acao} nada. Não há necessidade de {random.choice(['intervenção', 'ação', 'ajuste'])}. Apenas {random.choice(['registrando', 'informando', 'comunicando'])} que o caso está {random.choice(['resolvido', 'encerrado', 'finalizado'])}.",
            f"{saudacao}. Verificamos que o {sistema} estava {problema} mas {random.choice(['já não está mais', 'não está mais', 'parou de estar'])}. Os logs mostravam {erro} mas {random.choice(['parou de aparecer', 'não aparece mais', 'sumiu'])}. Não precisamos que vocês {acao} nada. Não há necessidade de {random.choice(['suporte', 'intervenção', 'ação'])}. Só {random.choice(['informando', 'comunicando', 'registrando'])} que está tudo {random.choice(['ok', 'normal', 'funcionando'])} agora.",
            f"{saudacao}, {destinatario}. O {sistema} estava {problema} mas {random.choice(['já não está mais', 'não está mais', 'parou de estar'])}. Não sabemos o que {random.choice(['causou', 'gerou', 'provocou'])} nem o que {random.choice(['resolveu', 'corrigiu', 'normalizou'])}, mas está {random.choice(['funcionando', 'operacional', 'estável'])} agora. Não precisamos que vocês {acao} nada. Não há necessidade de {random.choice(['intervenção', 'ação', 'ajuste'])}.",
            f"{saudacao}. O {sistema} estava {problema} mas {random.choice(['já não está mais', 'não está mais', 'parou de estar'])}. Fizemos uma {random.choice(['verificação', 'análise', 'investigação'])} e parece que {random.choice(['resolveu sozinho', 'estabilizou', 'normalizou'])}. Não precisamos que vocês {acao} nada. Não há necessidade de {random.choice(['suporte', 'intervenção', 'ação'])}. Apenas {random.choice(['informando', 'comunicando', 'registrando'])} que está tudo {random.choice(['ok', 'normal', 'funcionando'])}.",
        ]
    else:
        destinatario = random.choice(NOMES_EN)
        saudacao = random.choice(SAUDACOES_EN).replace("{name}", destinatario)
        no_longer_phrases = ["it's no longer", "it's not anymore", "it stopped being"]
        dont_need = "don't need"
        templates = [
            f"{saudacao}, {destinatario}. The {sistema} was {problema} but {random.choice(no_longer_phrases)}. We did a {random.choice(['trace', 'debug', 'analysis'])} and it seems {random.choice(['it resolved itself', 'it stabilized', 'it normalized'])}. We {dont_need} you to {acao} anything. There is no need for {random.choice(['intervention', 'action', 'adjustment'])}. Just {random.choice(['recording', 'informing', 'communicating'])} that the case is {random.choice(['resolved', 'closed', 'finished'])}.",
            f"{saudacao}. We verified that {sistema} was {problema} but {random.choice(no_longer_phrases)}. The logs showed {erro} but {random.choice(['it stopped appearing', 'it no longer appears', 'it disappeared'])}. We {dont_need} you to {acao} anything. There is no need for {random.choice(['support', 'intervention', 'action'])}. Just {random.choice(['informing', 'communicating', 'recording'])} that everything is {random.choice(['ok', 'normal', 'working'])} now.",
            f"{saudacao}, {destinatario}. The {sistema} was {problema} but {random.choice(no_longer_phrases)}. We do not know what {random.choice(['caused', 'generated', 'provoked'])} it nor what {random.choice(['resolved', 'fixed', 'normalized'])} it, but it is {random.choice(['working', 'operational', 'stable'])} now. We {dont_need} you to {acao} anything. There is no need for {random.choice(['intervention', 'action', 'adjustment'])}.",
            f"{saudacao}. The {sistema} was {problema} but {random.choice(no_longer_phrases)}. We did a {random.choice(['verification', 'analysis', 'investigation'])} and it seems {random.choice(['it resolved itself', 'it stabilized', 'it normalized'])}. We {dont_need} you to {acao} anything. There is no need for {random.choice(['support', 'intervention', 'action'])}. Just {random.choice(['informing', 'communicating', 'recording'])} that everything is {random.choice(['ok', 'normal', 'working'])}.",
        ]
    
    texto = random.choice(templates)
    
    return {
        "text": texto,
        "label": 0
    }


def generate_colloquial_technical_email() -> Dict:
    """Gera email produtivo com linguagem coloquial e técnica misturada."""
    lang = choose_language()
    nome, sobrenome, email, empresa = generate_random_person()
    sistema = random.choice(TERMOS_TECNICOS["sistemas"])
    problema = random.choice(TERMOS_TECNICOS["problemas"])
    erro = random.choice(TERMOS_TECNICOS["erros"])
    
    if lang == "pt":
        destinatario = random.choice(NOMES_PT)
        saudacao = random.choice(["Oi", "Olá", "E aí", "Fala", "Salve"]).replace("{nome}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}! O {sistema} {random.choice(['deu pau', 'travou', 'quebrou', 'parou de funcionar'])} aqui. Os logs mostram {erro} e não sei o que fazer. Pode {random.choice(['dar uma olhada', 'verificar', 'checar'])}? Preciso disso {random.choice(['urgente', 'pra ontem', 'com urgência'])}.",
            f"{saudacao}! O {sistema} está {problema} e está {random.choice(['atrapalhando', 'atrapalhando tudo', 'bloqueando'])} a operação aqui. Os logs mostram {erro} mas não entendo muito bem. Você pode {random.choice(['dar uma olhada', 'verificar', 'investigar'])} e me ajudar?",
            f"{saudacao}, {destinatario}. O {sistema} {random.choice(['deu problema', 'travou', 'quebrou'])} aqui. Os logs mostram {erro} e não consigo {random.choice(['resolver', 'consertar', 'corrigir'])} sozinho. Pode {random.choice(['dar uma olhada', 'verificar', 'checar'])} quando tiver um tempinho?",
            f"{saudacao}! O {sistema} está {problema} desde {random.choice(['ontem', 'hoje de manhã', 'há algumas horas'])} e está {random.choice(['atrapalhando', 'bloqueando', 'impactando'])} a operação. Os logs mostram {erro} mas não sei o que significa. Você pode {random.choice(['verificar', 'investigar', 'analisar'])} e me dizer o que fazer?",
            f"{saudacao}, {destinatario}. O {sistema} {random.choice(['parou de funcionar', 'travou', 'quebrou'])} aqui. Os logs mostram {erro} e não consigo {random.choice(['resolver', 'consertar', 'corrigir'])}. Pode {random.choice(['dar uma olhada', 'verificar', 'checar'])}? Preciso disso {random.choice(['urgente', 'com urgência', 'o quanto antes'])}.",
        ]
    else:
        destinatario = random.choice(NOMES_EN)
        saudacao = random.choice(["Hi", "Hey", "Hello", "Hi there", "Hey there"]).replace("{name}", destinatario)
        templates = [
            f"{saudacao}, {destinatario}! The {sistema} {random.choice(['crashed', 'froze', 'broke', 'stopped working'])} here. The logs show {erro} and I don't know what to do. Can you {random.choice(['take a look', 'check', 'verify'])}? I need this {random.choice(['urgent', 'asap', 'urgently'])}.",
            f"{saudacao}! The {sistema} is {problema} and it's {random.choice(['getting in the way', 'blocking everything', 'blocking'])} the operation here. The logs show {erro} but I don't understand it very well. Can you {random.choice(['take a look', 'check', 'investigate'])} and help me?",
            f"{saudacao}, {destinatario}. The {sistema} {random.choice(['had a problem', 'froze', 'broke'])} here. The logs show {erro} and I can't {random.choice(['fix', 'repair', 'correct'])} it alone. Can you {random.choice(['take a look', 'check', 'verify'])} when you have a moment?",
            f"{saudacao}! The {sistema} has been {problema} since {random.choice(['yesterday', 'this morning', 'a few hours ago'])} and it's {random.choice(['getting in the way', 'blocking', 'impacting'])} the operation. The logs show {erro} but I don't know what it means. Can you {random.choice(['check', 'investigate', 'analyze'])} and tell me what to do?",
            f"{saudacao}, {destinatario}. The {sistema} {random.choice(['stopped working', 'froze', 'broke'])} here. The logs show {erro} and I can't {random.choice(['fix', 'repair', 'correct'])} it. Can you {random.choice(['take a look', 'check', 'verify'])}? I need this {random.choice(['urgent', 'urgently', 'as soon as possible'])}.",
        ]
    
    texto = random.choice(templates)
    
    return {
        "text": texto,
        "label": 1
    }


def generate_urgent_productive_email() -> Dict:
    """Gera email produtivo urgente com termos técnicos."""
    lang = choose_language()
    nome, sobrenome, email, empresa = generate_random_person()
    sistema = random.choice(TERMOS_TECNICOS["sistemas"])
    problema = random.choice(TERMOS_TECNICOS["problemas"])
    erro = random.choice(TERMOS_TECNICOS["erros"])
    tecnologia = random.choice(TERMOS_TECNICOS["tecnologias"])
    
    if lang == "pt":
        templates = [
            f"URGENTE: O {sistema} parou de {random.choice(['classificar', 'processar', 'enviar', 'receber'])} os {random.choice(['e-mails', 'dados', 'registros', 'eventos'])} da {random.choice(['unidade', 'fábrica', 'planta'])} {random.choice(['Sul', 'Norte', 'Leste', 'Oeste'])}. Os logs mostram {erro} constante. Preciso que você verifique se houve alguma alteração na {tecnologia} ou se o servidor de vocês está em manutenção.",
            f"URGENTE: O {sistema} está {problema} desde {random.choice(['hoje de manhã', 'ontem à noite', 'há algumas horas'])}. A {random.choice(['produção', 'operação', 'linha de produção'])} está {random.choice(['parada', 'impactada', 'comprometida'])}. Precisamos de {random.choice(['suporte técnico', 'intervenção', 'correção'])} imediato.",
            f"URGENTE - {erro}: O {sistema} não está {random.choice(['respondendo', 'funcionando', 'processando'])}. A {random.choice(['API', 'integração', 'conexão'])} está {random.choice(['fora do ar', 'indisponível', 'com timeout'])}. Precisamos que vocês {random.choice(['verifiquem', 'investiguem', 'corrijam'])} isso {random.choice(['imediatamente', 'com urgência', 'o quanto antes'])}.",
            f"URGENTE: O {sistema} apresentou {erro} durante o {random.choice(['processamento', 'envio', 'sincronização'])} dos {random.choice(['dados', 'registros', 'eventos'])}. A {random.choice(['operação', 'produção', 'linha'])} está {random.choice(['parada', 'impactada'])}. Precisamos de {random.choice(['suporte', 'intervenção', 'correção'])} urgente.",
        ]
    else:
        templates = [
            f"URGENT: The {sistema} stopped {random.choice(['classifying', 'processing', 'sending', 'receiving'])} the {random.choice(['emails', 'data', 'records', 'events'])} from the {random.choice(['unit', 'factory', 'plant'])} {random.choice(['South', 'North', 'East', 'West'])}. The logs show constant {erro}. I need you to check if there was any change in {tecnologia} or if your server is under maintenance.",
            f"URGENT: The {sistema} has been {problema} since {random.choice(['this morning', 'last night', 'a few hours ago'])}. The {random.choice(['production', 'operation', 'production line'])} is {random.choice(['stopped', 'impacted', 'compromised'])}. We need {random.choice(['technical support', 'intervention', 'correction'])} immediately.",
            f"URGENT - {erro}: The {sistema} is not {random.choice(['responding', 'working', 'processing'])}. The {random.choice(['API', 'integration', 'connection'])} is {random.choice(['down', 'unavailable', 'with timeout'])}. We need you to {random.choice(['check', 'investigate', 'fix'])} this {random.choice(['immediately', 'urgently', 'as soon as possible'])}.",
            f"URGENT: The {sistema} presented {erro} during the {random.choice(['processing', 'sending', 'synchronization'])} of the {random.choice(['data', 'records', 'events'])}. The {random.choice(['operation', 'production', 'line'])} is {random.choice(['stopped', 'impacted'])}. We need {random.choice(['support', 'intervention', 'correction'])} urgently.",
        ]
    
    texto = random.choice(templates)
    
    return {
        "text": texto,
        "label": 1
    }


def generate_complex_training_data(
    num_productive: int = 3000,
    num_unproductive: int = 3000,
    output_file: str = "training_data_complex.json"
) -> None:
    """Gera dados de treinamento complexos e desafiadores."""
    print("=" * 70)
    print("Gerador de Dados de Treinamento Complexos e Desafiadores")
    print("=" * 70)
    
    emails = []
    
    # Distribuição dos tipos de emails produtivos (EXPANDIDO)
    num_ironic = num_productive // 8
    num_technical = num_productive // 6
    num_gratitude_request = num_productive // 8
    num_urgent = num_productive // 6
    num_confusing = num_productive // 8
    num_ambiguous = num_productive // 8
    num_mixed_context = num_productive // 8
    num_colloquial = num_productive // 8
    num_remaining = num_productive - (num_ironic + num_technical + num_gratitude_request + 
                                     num_urgent + num_confusing + num_ambiguous + 
                                     num_mixed_context + num_colloquial)
    
    print(f"\n📧 Gerando {num_productive} emails produtivos...")
    print(f"   - {num_ironic} emails com ironia/sarcasmo")
    print(f"   - {num_technical} emails técnicos detalhados")
    print(f"   - {num_gratitude_request} emails com agradecimento + solicitação")
    print(f"   - {num_urgent} emails urgentes")
    print(f"   - {num_confusing} emails confusos (múltiplas solicitações)")
    print(f"   - {num_ambiguous} emails ambíguos")
    print(f"   - {num_mixed_context} emails com contexto misturado")
    print(f"   - {num_colloquial} emails coloquiais/técnicos")
    print(f"   - {num_remaining} emails adicionais (distribuídos)")
    
    for _ in range(num_ironic):
        emails.append(generate_ironic_productive_email())
    
    for _ in range(num_technical):
        emails.append(generate_technical_productive_email())
    
    for _ in range(num_gratitude_request):
        emails.append(generate_gratitude_with_request_email())
    
    for _ in range(num_urgent):
        emails.append(generate_urgent_productive_email())
    
    for _ in range(num_confusing):
        emails.append(generate_confusing_productive_email())
    
    for _ in range(num_ambiguous):
        emails.append(generate_ambiguous_productive_email())
    
    for _ in range(num_mixed_context):
        emails.append(generate_mixed_context_email())
    
    for _ in range(num_colloquial):
        emails.append(generate_colloquial_technical_email())
    
    # Distribui os emails restantes entre os tipos
    remaining_types = [
        generate_ironic_productive_email,
        generate_technical_productive_email,
        generate_gratitude_with_request_email,
        generate_urgent_productive_email,
        generate_confusing_productive_email,
        generate_ambiguous_productive_email,
        generate_mixed_context_email,
        generate_colloquial_technical_email
    ]
    for _ in range(num_remaining):
        emails.append(random.choice(remaining_types)())
    
    # Distribuição dos tipos de emails não produtivos (EXPANDIDO)
    num_technical_unprod = num_unproductive // 4
    num_gratitude_unprod = num_unproductive // 4
    num_technical_but_unprod = num_unproductive // 4
    num_negation_complex = num_unproductive // 4
    
    print(f"\n📧 Gerando {num_unproductive} emails não produtivos...")
    print(f"   - {num_technical_unprod} emails técnicos informativos (sem ação)")
    print(f"   - {num_gratitude_unprod} emails de agradecimento/elogio")
    print(f"   - {num_technical_but_unprod} emails técnicos mas sem ação necessária")
    print(f"   - {num_negation_complex} emails com negações complexas")
    
    for _ in range(num_technical_unprod):
        emails.append(generate_technical_unproductive_email())
    
    for _ in range(num_gratitude_unprod):
        emails.append(generate_gratitude_unproductive_email())
    
    for _ in range(num_technical_but_unprod):
        emails.append(generate_technical_but_unproductive_email())
    
    for _ in range(num_negation_complex):
        emails.append(generate_negation_complex_email())
    
    # Embaralha os emails
    random.shuffle(emails)
    
    # Salva em JSON
    print(f"\n💾 Salvando {len(emails)} emails em {output_file}...")
    # Cria o diretório se não existir
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(emails, f, ensure_ascii=False, indent=2)
    
    # Estatísticas
    from collections import Counter
    label_counts = Counter(email["label"] for email in emails)
    
    print("\n" + "=" * 70)
    print("📊 Estatísticas:")
    print("=" * 70)
    print(f"Total de emails gerados: {len(emails)}")
    print(f"  - Produtivos (label 1): {label_counts[1]}")
    print(f"  - Não produtivos (label 0): {label_counts[0]}")
    print(f"\n💾 Arquivo salvo em: {output_file}")
    print("\n✅ Geração de dados complexos concluída!")
    print("\n💡 Características dos dados gerados:")
    print("   ✓ Emails em PORTUGUÊS e INGLÊS (geração bilíngue aleatória)")
    print("   ✓ Vocabulário técnico MUITO diversificado (300+ termos únicos)")
    print("   ✓ Emails com ironia/sarcasmo (casos edge case)")
    print("   ✓ Agradecimentos seguidos de solicitações")
    print("   ✓ Emails confusos com múltiplas solicitações misturadas")
    print("   ✓ Emails ambíguos que podem parecer não produtivos")
    print("   ✓ Emails com contexto misturado (agradecimento + problema + solicitação)")
    print("   ✓ Emails coloquiais com linguagem técnica")
    print("   ✓ Termos técnicos em contextos não produtivos")
    print("   ✓ Emails com negações complexas de ações")
    print("   ✓ Referências a clientes e tecnologias específicas")
    print("   ✓ Variação de tom (formal, informal, técnico, coloquial)")
    print("   ✓ Casos MUITO complexos que desafiam ao máximo o modelo")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gera dados de treinamento complexos e desafiadores"
    )
    parser.add_argument(
        "--productive",
        type=int,
        default=3000,
        help="Número de emails produtivos a gerar (padrão: 3000)"
    )
    parser.add_argument(
        "--unproductive",
        type=int,
        default=3000,
        help="Número de emails não produtivos a gerar (padrão: 3000)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="training_data.pt-en.json",
        help="Arquivo de saída (padrão: training_data.json)"
    )
    
    args = parser.parse_args()
    
    random.seed(42)  # Para reprodutibilidade
    generate_complex_training_data(
        num_productive=args.productive,
        num_unproductive=args.unproductive,
        output_file=args.output
    )

