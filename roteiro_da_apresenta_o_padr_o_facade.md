# Roteiro de Apresentação: Design Pattern Facade (Aplicado a Pipeline de Dados)

Esta estrutura foi desenhada para **5 apresentadores**, garantindo que cada pessoa tenha um tempo de fala equilibrado e uma transição lógica entre a teoria (Parte 1), o problema e a solução prática no pipeline de dados (Partes 2, 3 e 4) e a análise crítica final (Parte 5).

---

## 👤 Parte 1: Fundamentação Teórica e Diferenciação (Pessoa 1)

**Objetivo:** Introduzir o conceito do padrão Facade de forma clara (baseado no *Refactoring Guru*) e diferenciá-lo de outros padrões parecidos para evitar confusões comuns.

### Tópicos a abordar:
1. **O que é o Facade (Fachada)?**
   * **Definição:** É um padrão de projeto estrutural que fornece uma interface simplificada para uma biblioteca, um framework ou qualquer conjunto complexo de classes (subsistema).
   * **Analogia do Mundo Real:** Fazer um pedido por telefone ou aplicativo em uma loja. O atendente (ou a tela do app) é a "fachada" para todo o sistema complexo de verificação de estoque, gateway de pagamento, faturamento e logística de entrega.
2. **Qual é o propósito principal?**
   * Desacoplar o código do **Cliente** (quem usa) da complexidade do **Subsistema** (como funciona por baixo dos panos).
   * Aplicação direta do *Princípio do Menor Conhecimento* (Lei de Demeter): o cliente só conversa com seu "amigo direto" (o Facade).
3. **Diferença entre padrões parecidos (Comparativo Rápido):**
   * **Facade vs. Adapter:** O *Facade* define uma **nova interface simplificada** para um subsistema inteiro; o *Adapter* envolve apenas um objeto para fazer uma interface antiga/incompatível **funcionar com outra** esperada pelo sistema.
   * **Facade vs. Mediator:** O *Mediator* centraliza a comunicação **bidirecional entre** vários componentes que não devem conversar diretamente; o *Facade* apenas cria um atalho **unidirecional** de fora para dentro do subsistema, sem alterar como os subsistemas funcionam internamente.
   * **Facade vs. Abstract Factory:** O *Abstract Factory* esconde como famílias de objetos são **instanciadas/criadas**; o *Facade* esconde como objetos complexos **operam em conjunto** para realizar uma tarefa.

---

## 👤 Parte 2: O Cenário do Pipeline de Dados e o "Caos" Sem Facade (Pessoa 2)

**Objetivo:** Apresentar o caso prático (Pipeline de Dados / ETL) e mostrar na prática o código e os problemas de **não** utilizar o padrão Facade.

### Tópicos a abordar:
1. **Apresentação do Subsistema Complexo (O Pipeline de Dados):**
   * Explicar as classes independentes que compõem o pipeline de dados da empresa:
     1. `DatabaseExtractor`: Conecta ao banco de dados e extrai dados brutos.
     2. `DataCleaner`: Remove valores nulos, duplicatas e corrige tipos de dados.
     3. `BusinessTransformer`: Aplica cálculos de negócio, agregações e normalização.
     4. `ParquetExporter`: Converte os dados processados para o formato `.parquet`.
     5. `CloudStorageUploader`: Envia o arquivo final para a nuvem (ex: AWS S3 ou Google Cloud Storage) e emite notificação.
2. **Demonstração: O Código SEM o Facade:**
   * Mostrar na tela como o **Cliente** (ex: um endpoint de uma API ou um script agendado) precisa chamar e coordenar todas essas classes manualmente.
   * Explicar que o cliente precisa saber a ordem exata: conectar, extrair, passar o resultado para o limpador, passar para o transformador, gerar o arquivo e fechar a conexão.
3. **Dores visíveis nessa abordagem:**
   * **Alto Acoplamento:** O código do cliente conhece detalhes íntimos de 5 classes diferentes.
   * **Duplicação de Código (Violação do DRY):** Se esse pipeline precisar ser executado por uma API Web, por um terminal (CLI) e por um robô agendado (Cronjob), toda essa sequência de 15 linhas terá que ser copiada e colada nos três lugares.
   * **Fragilidade:** Se a equipe de dados adicionar uma etapa nova (ex: `DataValidator`), será necessário alterar todos os clientes que rodam o pipeline.

---

## 👤 Parte 3: Arquitetura da Solução e Construção do Facade (Pessoa 3)

**Objetivo:** Mostrar o desenho arquitetural do padrão aplicado ao pipeline e construir a classe `DataPipelineFacade` por dentro.

### Tópicos a abordar:
1. **Mapeando o Padrão (UML do Pipeline):**
   * Mostrar o diagrama do *Refactoring Guru* adaptado ao projeto:
     * **Subsistema:** `DatabaseExtractor`, `DataCleaner`, `BusinessTransformer`, `ParquetExporter`, `CloudStorageUploader`.
     * **Facade:** `DataPipelineFacade`.
     * **Facade Adicional (Opcional):** Mencionar que, se o subsistema for gigante, o Facade pode usar sub-facades (ex: `IngestionFacade` e `ExportFacade`).
2. **Construindo a classe `DataPipelineFacade` passo a passo:**
   * **Atributos e Construtor:** Mostrar como o Facade guarda as referências para os módulos do pipeline (seja instanciando-os ou recebendo via Injeção de Dependência).
   * **O Método Simplificador (`run_pipeline`):** Mostrar como toda aquela orquestração complexa (extrair -> limpar -> transformar -> exportar -> subir para a nuvem) agora mora **dentro** de um único método do Facade.
3. **Transparência do Subsistema:**
   * Destacar um ponto fundamental da teoria: **As classes do subsistema não sabem que o Facade existe.** Elas continuam fazendo seu trabalho isolado exatamente da mesma forma.

---

## 👤 Parte 4: O Pipeline COM Facade em Ação e Flexibilidade (Pessoa 4)

**Objetivo:** Comparar o código do cliente (Antes vs. Depois) e demonstrar como o Facade lida com diferentes necessidades sem "prender" o desenvolvedor.

### Tópicos a abordar:
1. **Comparativo Direto no Cliente (Antes vs. Depois):**
   * Mostrar como o código do cliente (API, CLI ou Cronjob) caiu de dezenas de linhas acopladas para apenas **duas linhas**: instanciar o `DataPipelineFacade` e chamar `facade.run_pipeline(origem, destino)`.
2. **Evolução sem dor (Manutenibilidade):**
   * Simular uma mudança: *"E se agora precisarmos adicionar uma etapa de criptografia (`DataEncryptor`) ou um envio de log para o Slack antes de finalizar?"*
   * Mostrar que alteramos **apenas** o método dentro do `DataPipelineFacade`, e todos os clientes passam a usar a nova regra automaticamente sem alterar uma linha de código neles.
3. **E se um cliente avançado precisar de algo específico? (Acesso Direto):**
   * Explicar que o Facade **não esconde ou bloqueia** o subsistema, ele apenas oferece um caminho padrão simplificado.
   * Exemplo no pipeline: Se um Cientista de Dados quiser usar apenas o `DataCleaner` em um arquivo local para um teste rápido, ele ainda pode chamar o `DataCleaner` diretamente, enquanto o sistema de produção usa o `DataPipelineFacade`.

---

## 👤 Parte 5: Vantagens, Dificuldades, Principais Erros e Como Corrigi-los (Pessoa 5)

**Objetivo:** Fechar a apresentação com uma visão sênior e crítica sobre o padrão, mostrando benefícios reais, armadilhas de implementação e soluções de refatoração.

### Tópicos a abordar:
1. **Principais Vantagens:**
   * **Isolamento da Complexidade:** O código de negócio/cliente fica limpo e legível.
   * **Facilidade de Testes e Mudança de Subsistema:** Se trocarmos a biblioteca de processamento (ex: de *Pandas* para *Polars* ou *PySpark* internamente), o cliente nem fica sabendo, pois a assinatura do Facade continua a mesma.
2. **Dificuldades de Implementação:**
   * **Definir a fronteira certa:** Saber exatamente o que deve entrar no Facade e o que deve ficar de fora para não criar métodos com 20 parâmetros.
   * **Gestão de Erros:** Como traduzir exceções muito específicas do subsistema (ex: erro de ponteiro no Parquet) em um erro compreensível para o cliente.
3. **Principais Erros (Anti-patterns) e Como Corrigi-los:**
   * ❌ **Erro 1: A "God Class" (Classe Deus / Objeto Faz-Tudo):**
     * *O que é:* O Facade começa a crescer tanto e acumular tantas responsabilidades que ele passa a conhecer todas as classes do sistema inteiro.
     * *Como corrigir:* Dividir o Facade grande em **Facades menores e especializados** (ex: criar um `BatchPipelineFacade` e um `StreamingPipelineFacade`) ou aplicar o *Princípio da Segregação de Interface (ISP)*.
   * ❌ **Erro 2: Colocar Regra de Negócio dentro do Facade:**
     * *O que é:* Começar a fazer `if/else` de cálculo de imposto ou limpeza de string diretamente dentro do método do Facade, em vez de delegar para as classes do subsistema.
     * *Como corrigir:* O Facade deve ser estritamente um **orquestrador/delegador**. Mova qualquer lógica de transformação de volta para a classe `BusinessTransformer`.
   * ❌ **Erro 3: Forte Acoplamento na Instanciação (`new` fixo no construtor):**
     * *O que é:* Instanciar bancos de dados e serviços de nuvem diretamente dentro do construtor do Facade, impossibilitando testes unitários com *Mocks*.
     * *Como corrigir:* Usar **Injeção de Dependência** (passar as instâncias pelo construtor ou usar uma *Factory*), permitindo testar o Facade sem precisar conectar no banco de dados real.

---

## 💻 Anexo: Código de Exemplo (Python) para os Slides (Partes 2, 3 e 4)

Vocês podem colocar esses blocos nos slides para ilustrar o pipeline:

### 1. O Subsistema Complexo (Usado em ambos os casos)
```python
class DatabaseExtractor:
    def connect(self, uri: str): print(f"Conectando em {uri}...")
    def fetch_raw_data(self, query: str) -> list:
        print("Extraindo dados brutos...")
        return [{"id": 1, "val": None}, {"id": 2, "val": 100}]

class DataCleaner:
    def remove_nulls(self, data: list) -> list:
        print("Limpando dados nulos...")
        return [row for row in data if row["val"] is not None]

class BusinessTransformer:
    def apply_rules(self, data: list) -> list:
        print("Aplicando regras de negócio e agregações...")
        return [{"id": r["id"], "total": r["val"] * 1.15} for r in data]

class ParquetExporter:
    def to_parquet(self, data: list) -> str:
        print("Convertendo para formato Parquet...")
        return "/tmp/output_data.parquet"

class CloudStorageUploader:
    def upload(self, file_path: str, bucket: str):
        print(f"Enviando {file_path} para o bucket {bucket} na nuvem!")
```

### 2. Cenário SEM Facade (Slide da Pessoa 2)
```python
# O Cliente precisa conhecer, instanciar e coordenar TUDO manualmente:
def endpoint_rodar_relatorio():
    extractor = DatabaseExtractor()
    cleaner = DataCleaner()
    transformer = BusinessTransformer()
    exporter = ParquetExporter()
    uploader = CloudStorageUploader()

    # Alta chance de esquecer uma etapa ou errar a ordem:
    extractor.connect("postgres://prod-db:5432")
    raw_data = extractor.fetch_raw_data("SELECT * FROM vendas")
    clean_data = cleaner.remove_nulls(raw_data)
    transformed_data = transformer.apply_rules(clean_data)
    parquet_file = exporter.to_parquet(transformed_data)
    uploader.upload(parquet_file, "s3://meu-datalake-prod")
```

### 3. Cenário COM Facade (Slides das Pessoas 3 e 4)
```python
# PESSOA 3: A Classe Facade encapsulando a complexidade
class DataPipelineFacade:
    def __init__(self, db_uri: str, target_bucket: str):
        self.db_uri = db_uri
        self.target_bucket = target_bucket
        # Subsistema inicializado internamente
        self.extractor = DatabaseExtractor()
        self.cleaner = DataCleaner()
        self.transformer = BusinessTransformer()
        self.exporter = ParquetExporter()
        self.uploader = CloudStorageUploader()

    def run_etl_pipeline(self, query: str):
        print("--- Iniciando Pipeline via Facade ---")
        self.extractor.connect(self.db_uri)
        raw = self.extractor.fetch_raw_data(query)
        clean = self.cleaner.remove_nulls(raw)
        transformed = self.transformer.apply_rules(clean)
        file_path = self.exporter.to_parquet(transformed)
        self.uploader.upload(file_path, self.target_bucket)
        print("--- Pipeline Finalizado com Sucesso! ---")


# PESSOA 4: O Cliente agora fica extremamente simples e desacoplado
def endpoint_rodar_relatorio():
    pipeline = DataPipelineFacade("postgres://prod-db:5432", "s3://meu-datalake-prod")
    pipeline.run_etl_pipeline("SELECT * FROM vendas")
```