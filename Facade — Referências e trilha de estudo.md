---
tipo: trabalho
disciplina: "[[Engenharia de Software]]"
tema: Design Pattern Facade
status: em andamento
criado: 2026-10-21
---

# Facade — Referências e trilha de estudo

Trabalho de [[Engenharia de Software]] sobre o padrão **Facade (Fachada)**, com base no Refactoring Guru. **Parte prática:** apresentar um pipeline de dados feito de duas formas, com e sem Facade. Escolhemos um ETL de dados climáticos. Ele está em [pipeline-clima](pipeline-clima/README.md). Padrões anteriores da disciplina: [[Design Patterns — Notas de Aula]].

## A ideia em uma tela

**Facade** é um padrão *estrutural*: uma classe oferece uma interface **simples (e limitada)** para um subsistema complicado. O cliente chama um método; a fachada instancia objetos, resolve dependências e chama tudo na ordem certa.

Exemplo concreto do Refactoring Guru: converter vídeo com um framework de terceiros exige `VideoFile`, `CodecFactory`, `BitrateReader`, `AudioMixer`... A fachada `VideoConverter.convert("gatos.ogg", "mp4")` esconde tudo isso. Se o framework mudar, só a fachada é reescrita.

```python
class VideoConverter:                      # Fachada
    def convert(self, filename, fmt):
        file = VideoFile(filename)
        src = CodecFactory.extract(file)
        dst = MPEG4Codec() if fmt == "mp4" else OggCodec()
        buf = BitrateReader.read(file, src)
        out = BitrateReader.convert(buf, dst)
        return AudioMixer().fix(out)

# Cliente: não conhece o subsistema
VideoConverter().convert("gatos.ogg", "mp4")
```

**Participantes:** Fachada · Fachada adicional (evita que uma só fachada vire "objeto deus") · Subsistema complexo (não sabe que a fachada existe) · Cliente.

**Prós e contras:** isola o cliente da complexidade e concentra dependências indesejadas num lugar só. O risco é a fachada crescer e se acoplar a tudo (*god object*, *Large Class*).

**Comparações que costumam cair:**

| Padrão | Diferença para o Facade |
|---|---|
| Adapter | Adapter faz uma interface **existente** funcionar (em geral um objeto); Facade **cria uma interface nova** para um subsistema inteiro |
| Mediator | Mediator centraliza a comunicação e os componentes só conhecem o mediador; no Facade, o subsistema não sabe da fachada e as classes continuam se falando |
| Proxy | Proxy tem a **mesma interface** do objeto real e é intercambiável com ele; Facade não |
| Abstract Factory | Pode substituir o Facade quando a meta é só esconder a criação dos objetos — liga com [[abstract_factory.py]] |
| Singleton | Uma fachada costuma ser única, então pode virar Singleton |

Princípio associado: **Princípio do Menor Conhecimento (Lei de Deméter)** — "fale só com seus amigos imediatos". O Facade é o exemplo clássico dele (Head First, cap. 7).

## Facades que você já usa em Python

Útil para a parte prática e para a apresentação: ninguém precisa inventar exemplo artificial.

- `requests.get(url)` — esconde `Session`, `PreparedRequest`, adaptadores HTTP e pool de conexões do `urllib3`.
- `subprocess.run(...)` — fachada sobre `Popen`, `communicate()`, `wait()` e checagem do código de saída.
- `pandas.read_csv(...)` — um chamado escolhe engine, parser, inferência de tipos e montagem do `DataFrame`.
- `shutil.copytree` / `shutil.make_archive` — orquestram várias chamadas de `os` e `zipfile`/`tarfile`.

Exercício de olhar: abrir o código-fonte de `requests/api.py` e ver que `get` só cria uma sessão e delega.

## Referências

### Base do trabalho

- **Refactoring Guru — Facade (pt-BR):** https://refactoring.guru/pt-br/design-patterns/facade — problema, solução, estrutura, aplicabilidade, passos de implementação e relações.
- **Refactoring Guru — exemplo conceitual em Python:** https://refactoring.guru/pt-br/design-patterns/facade/python/example — `Facade`, `Subsystem1`, `Subsystem2`, `client_code`. Há versões em C#, C++, Go, Java, PHP, Ruby, Rust, Swift e TypeScript.

### Livros (fonte primária e didática)

- **Gamma, Helm, Johnson, Vlissides (GoF), *Design Patterns: Elements of Reusable Object-Oriented Software*, 1994.** Definição original: interface unificada para um conjunto de interfaces de um subsistema. Em português: *Padrões de Projeto: Soluções Reutilizáveis de Software Orientado a Objetos* (Bookman). Bom para citar no trabalho.
- **Freeman & Robson, *Head First Design Patterns* (2ª ed., 2020), cap. 7 "Adapter e Facade".** Exemplo do *home theater*: assistir a um filme exige várias operações manuais, e `HomeTheaterFacade.watchMovie()` resume tudo. Também traz o Princípio do Menor Conhecimento. Em português: *Use a Cabeça! Padrões de Projetos* (Alta Books). O mais didático da lista.
- **Lott & Phillips, *Python Object-Oriented Programming* (4ª ed., Packt), capítulo de padrões estruturais.** Facade em Python idiomático, com a distinção para Adapter. Versão em curso: https://www.devpath.com/courses/building-robust-object-oriented-python-apps-and-libraries/the-facade-pattern

### Código para estudar

- **faif/python-patterns — `facade.py`:** https://github.com/faif/python-patterns/blob/master/patterns/structural/facade.py — exemplo curto e executável, analogia do botão de ligar o computador.
- **DEV Community — Facade em Python:** https://dev.to/bshadmehr/simplifying-complex-systems-with-the-facade-design-pattern-in-python-206h — `CloudServiceFacade` junta autenticação e upload num `authenticate_and_upload`.

### Material de aula de outras universidades

- **UAH (CS307) — Facade:** https://www.cs.uah.edu/~rcoleman/CS307/DesignPatterns/DP09-Facade.html
- **Colorado (CSCI 6448) — slides de Adapter/Facade, baseados no Head First:** https://home.cs.colorado.edu/~kena/classes/6448/s05/lectures/lecture21.pdf
- **IFPR — Frameworks, aula 08 (pt-BR):** https://wiki.foz.ifpr.edu.br/wiki/images/7/70/Tads-frameworks-aula-08-facade.pdf — fachada para CPU, memória, HD e vídeo.
- **Marcel Santos — "Padrões de projeto: Facade em linguagens dinâmicas" (slides, pt-BR):** https://speakerdeck.com/marcelgsantos/padroes-de-projeto-facade-em-linguagens-dinamicas

### Para ir além (arquitetura)

- **Martin Fowler — Gateway:** https://martinfowler.com/eaaCatalog/gateway.html — parente do Facade para recursos **externos** (APIs, banco). Liga com o eixo de APIs e integração da [[Ementa — Engenharia de Software]].
- **Wikipedia — Facade pattern:** https://en.wikipedia.org/wiki/Facade_pattern — panorama e histórico.

## Projeto prático — pipeline de clima

Pasta `pipeline-clima/`, criada em 24/10/2026. Fluxo: extrair (API Open-Meteo ou CSV) → validar → limpar → agregar por mês → SQLite → relatório.

- Versão **go horse:** `notebooks/01_go_horse.ipynb`. Com o CSV sujo, a máxima média de SP em janeiro sai 59,2 °C e ninguém percebe.
- Versão **com Facade:** pacote `clima/` com a fachada `PipelineClima.executar(cidades, inicio, fim)`, o cliente `main.py`, o notebook `02_com_facade.ipynb` e 5 testes offline.
- Roteiro da demonstração no README do projeto.

- [ ] Rodar os dois notebooks e anotar uma dúvida sobre a fachada #es
- [ ] Levar o projeto ao grupo e dividir: demo do go horse, demo da fachada, slides de teoria #es
- [ ] Decidir se vale criar uma fachada adicional (`RelatorioFacade`) para mostrar o participante #es

## Trilha de estudo

- [ ] Ler a página do Refactoring Guru até "Estrutura" e anotar com suas palavras o problema que o Facade resolve #es ⏳ 2026-10-21
- [ ] Rodar o exemplo conceitual em Python do Refactoring Guru e trocar `Subsystem2` por um subsistema inventado #es
- [ ] Ler o cap. 7 do Head First (parte do Facade) e montar a tabela Facade × Adapter × Mediator com exemplo próprio #es
- [ ] Abrir `requests/api.py` e identificar fachada, subsistema e cliente #es
- [ ] Receber o enunciado e a parte prática; quebrar em micro-passos aqui #es
