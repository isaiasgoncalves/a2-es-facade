from abc import ABC, abstractmethod


class Iluminacao(ABC):
    @abstractmethod
    def intensidade(self, nivel: int) -> None: ...

    @abstractmethod
    def acender(self) -> None: ...


class ExibidorVideo(ABC):
    @abstractmethod
    def ligar(self) -> None: ...

    @abstractmethod
    def modo_widescreen(self) -> None: ...

    @abstractmethod
    def desligar(self) -> None: ...


class SistemaAudio(ABC):
    @abstractmethod
    def ligar(self) -> None: ...

    @abstractmethod
    def definir_volume(self, volume: int) -> None: ...

    @abstractmethod
    def desligar(self) -> None: ...


class ReprodutorMidia(ABC):
    @abstractmethod
    def ligar(self) -> None: ...

    @abstractmethod
    def reproduzir(self, filme: str) -> None: ...

    @abstractmethod
    def parar(self) -> None: ...

    @abstractmethod
    def desligar(self) -> None: ...


class Luzes(Iluminacao):
    def intensidade(self, nivel: int) -> None:
        print(f"Luzes ajustadas para {nivel}%.")

    def acender(self) -> None:
        print("Luzes acesas em 100%.")


class Projetor(ExibidorVideo):
    def ligar(self) -> None:
        print("Projetor ligado.")

    def modo_widescreen(self) -> None:
        print("Projetor configurado em modo widescreen (16:9).")

    def desligar(self) -> None:
        print("Projetor desligado.")


class SistemaDeSom(SistemaAudio):
    def ligar(self) -> None:
        print("Sistema de som ligado.")

    def definir_volume(self, volume: int) -> None:
        print(f"Volume definido para {volume}.")

    def desligar(self) -> None:
        print("Sistema de som desligado.")


class StreamingPlayer(ReprodutorMidia):
    def ligar(self) -> None:
        print("Streaming Player ligado.")

    def reproduzir(self, filme: str) -> None:
        print(f"Reproduzindo '{filme}' via streaming.")

    def parar(self) -> None:
        print("Reprodução interrompida.")

    def desligar(self) -> None:
        print("Streaming Player desligado.")


class BluRayPlayer(ReprodutorMidia):
    def ligar(self) -> None:
        print("Blu-ray Player ligado.")

    def reproduzir(self, filme: str) -> None:
        print(f"Lendo disco e reproduzindo '{filme}'.")

    def parar(self) -> None:
        print("Disco parado.")

    def desligar(self) -> None:
        print("Blu-ray Player desligado.")


class SalaDeCinemaFacade:
    def __init__(
        self,
        luzes: Iluminacao,
        projetor: ExibidorVideo,
        som: SistemaAudio,
        player: ReprodutorMidia,
    ) -> None:
        self._luzes = luzes
        self._projetor = projetor
        self._som = som
        self._player = player

    def assistir_filme(
        self, filme: str, volume: int = 20, nivel_luz: int = 15
    ) -> None:
        print(f"####### Preparando sessão: {filme} #######")
        self._luzes.intensidade(nivel_luz)
        self._projetor.ligar()
        self._projetor.modo_widescreen()
        self._som.ligar()
        self._som.definir_volume(volume)
        self._player.ligar()
        self._player.reproduzir(filme)

    def encerrar_filme(self) -> None:
        print("####### Encerrando sessão #######")
        self._player.parar()
        self._player.desligar()
        self._som.desligar()
        self._projetor.desligar()
        self._luzes.acender()


def main() -> None:
    sala_streaming = SalaDeCinemaFacade(
        luzes=Luzes(),
        projetor=Projetor(),
        som=SistemaDeSom(),
        player=StreamingPlayer(),
    )
    sala_streaming.assistir_filme("Vingadores: Doutor Destino")
    sala_streaming.encerrar_filme()

    sala_bluray = SalaDeCinemaFacade(
        luzes=Luzes(),
        projetor=Projetor(),
        som=SistemaDeSom(),
        player=BluRayPlayer(),
    )
    sala_bluray.assistir_filme("Duna: Parte Três", volume=30, nivel_luz=10)
    sala_bluray.encerrar_filme()


if __name__ == "__main__":
    main()