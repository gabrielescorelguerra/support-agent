# Fluxo

- *Webhook* recebe a mensagem, classifica por meio de métodos determinísticos e LLM, gerando resposta com base na classificação
	- Também identifica informações como tom, sistema, situação... para uso posterior
	- Para respostas mais simples, usa *templates* pré-definidos, com prevenção de repetição

## Fluxo geral

```mermaid
---
title: Fluxo Geral
---
flowchart TB

%%{init: { 'flowchart': { 'curve': 'smooth', 'nodeSpacing': 20, 'padding': 5 }, 'theme': 'base', 'themeVariables': { 'primaryTextColor': '#333333', 'edgeLabelBackground': '#ffffff' } }}%%

%% =========================

  

%% ESTILOS

  

%% =========================

classDef user fill:#e9ecef,stroke:#ced4da,color:#212529
classDef agent fill:#e8eaf6,stroke:#7986cb,color:#1a237e
classDef whatsapp fill:#e8f5e9,stroke:#a5d6a7,color:#1b5e20
classDef tiflux fill:#fff3e0,stroke:#ffcc80,color:#e65100
classDef ia fill:#f3e5f5,stroke:#ce93d8,color:#4a148c
  
style INT fill:#ffffff,stroke:#ce93d8,color:#4a148c

%% =========================

  

%% USUÁRIO / WHATSAPP

  

%% =========================

  

U[Usuário]

Wh[WhatsApp]

  

%% =========================

  

%% TIFLUX

  

%% =========================

TIFLUX[TiFlux]

%% =========================  
%% INTEGRAÇÃO IA  
%% =========================    

subgraph INT[Integração IA]
    
    WEB[Webhook Endpoint]

    ROUTER[Roteador]  
    TRIAGE_AGENT[Agente de Triagem]

    RES[Resposta]
    
    WEB --> ROUTER --> TRIAGE_AGENT
  
    TRIAGE_AGENT --> RES

end    
%% =========================
%% FLUXO EXTERNO
%% =========================

U --> Wh

Wh --> TIFLUX --> WEB

RES --> WEB

WEB --> TIFLUX --> Wh

Wh --> U

%% =========================

%% CLASSES

%% =========================

class WEB,RES,KNOW_DB,RAG,CONTEXT,SYS_PROMPT,ROUTER ia
class U user
class Wh whatsapp
class TIFLUX tiflux
class TRIAGE_AGENT agent
```

## Agente de triagem

```mermaid
---
title: Agente de Triagem
---
%%{init: { 'flowchart': { 'curve': 'smooth', 'nodeSpacing': 20, 'padding': 5 }, 'theme': 'base', 'themeVariables': { 'primaryTextColor': '#333333', 'edgeLabelBackground': '#ffffff' } }}%%
flowchart TB

    %% =========================
    %% ESTILOS
    %% =========================

    classDef ia fill:#f3e5f5,stroke:#ce93d8,color:#4a148c
    classDef agent fill:#e8eaf6,stroke:#7986cb,color:#1a237e
    classDef mainAgent fill:#c5cae9,stroke:#3f51b5,color:#000051

    style TA fill:#ffffff,stroke:#3f51b5,color:#1a237e
    style PATH_SUB fill:#ffffff,stroke:#7986cb,color:#1a237e
    style DEFINE_SUB fill:#ffffff,stroke:#7986cb,color:#1a237e

    %% =========================
    %% ENTRADA EXTERNA
    %% =========================

    R[Roteador]

    %% =========================
    %% SUBGRAPH PRINCIPAL: AGENTE DE TRIAGEM
    %% =========================

    subgraph TA[Agente de Triagem]

        %% Subgraph: Classificação de Caminho %%
        subgraph PATH_SUB[Identificação de Caminho]
            LLM_PATH[LLM]
            RES_JSON[Resultado da Análise - JSON]

            LLM_PATH --> RES_JSON
        end

        %% Subgraph: Refinamento / Nova Pergunta %%
        subgraph DEFINE_SUB[Refinamento de Dúvida]
	        IS_SIMPLE{Resposta Simples?}
            LLM_DEFINE[LLM]
            RES_BD[Respostas Prontas]
            RES_DEFINE[Nova Pergunta de Refinamento]

            IS_SIMPLE -- "Não" --> LLM_DEFINE --> RES_DEFINE
            IS_SIMPLE -- "Sim" --> RES_BD --> RES_DEFINE
        end

        RES_TRANSFER[Mensagem de Transferência]

        %% Decisão baseada na confiança %%
        RES_JSON -- "Confiança Suficiente" --> RES_TRANSFER
        RES_JSON -- "Pouca Confiança" --> IS_SIMPLE

    end

    %% =========================
    %% SAÍDA EXTERNA (ROSA)
    %% =========================

    RES[Resposta]

    %% =========================
    %% CONEXÕES DE ENTRADA E SAÍDA
    %% =========================

    R --> LLM_PATH

    RES_DEFINE --> RES
    RES_TRANSFER --> RES

    RES -.-> R

    %% =========================
    %% CLASSES
    %% =========================

    class R,RES ia
    class LLM_PATH,RES_JSON,LLM_DEFINE,RES_DEFINE,RES_TRANSFER,IS_SIMPLE,RES_BD agent
```
