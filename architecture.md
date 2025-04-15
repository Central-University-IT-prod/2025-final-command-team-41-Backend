# Архитектура системы бронирования коворкинга

Бэкенд-сервис для системы бронирования коворкинга на Python с FastAPI.
## Ключевые архитектурные принципы

- **Чистая архитектура**: Разделение ответственности между слоями домена, приложения и инфраструктуры
- **DDD (Domain-Driven Design)**: Бизнес-логика организована вокруг доменов с явными границами
- **Внедрение зависимостей**: Использует фреймворк dishka для DI
- **Событийно-ориентированное взаимодействие**: Сервисы взаимодействуют через шину событий
- **Модульная структура**: Функциональность разделена на связанные модули с четкими интерфейсами
### Архитектурные паттерны

- **Репозиторий**: Абстрагирует логику доступа к данным
- **CQRS**: Разделяет операции чтения и записи
- **Инверсия зависимостей**: Высокоуровневые модули не зависят от низкоуровневых
- **Сервисный слой**: Координирует действия между репозиториями и доменом
## Структура проекта

```
backend/
├── src/
│   ├── core/                  # Основная функциональность, используемая во всех модулях
│   │   ├── container.py       # Контейнер внедрения зависимостей
│   │   ├── database.py        # Подключение к базе данных и управление сессиями
│   │   ├── di.py              # Провайдеры внедрения зависимостей
│   │   ├── domain.py          # Базовые доменные сущности и интерфейсы
│   │   ├── error_handlers.py  # Обработчики ошибок для FastAPI
│   │   ├── events.py          # Реализация шины событий
│   │   ├── exceptions.py      # Централизованная обработка исключений
│   │   ├── factories.py       # Фабрики для создания сервисов
│   │   ├── logging.py         # Утилиты для логирования
│   │   ├── settings.py        # Конфигурация приложения
│   │   └── timezone_utils.py  # Утилиты для работы с временными зонами
│   │
│   ├── modules/               # Модули, специфичные для предметной области
│   │   ├── auth/              # Модуль аутентификации
│   │   ├── base/              # Базовый модуль с общими компонентами
│   │   ├── bookings/          # Модуль бронирований
│   │   ├── coworkings/        # Модуль коворкингов
│   │   ├── healthcheck/       # Модуль проверки работоспособности
│   │   ├── notifications/     # Модуль уведомлений
│   │   ├── options/           # Модуль опций
│   │   ├── spots/             # Модуль мест
│   │   ├── storage/           # Модуль хранилища
│   │   └── users/             # Модуль пользователей
│   │
│   ├── entrypoints/           # Точки входа в приложение
│   │   ├── mock/              # Мок данные для разработки и тестирования
│   │   ├── rest/              # REST API сервер (FastAPI)
│   │   └── runner/            # Обработчик событий
│   │
│   └── tests/                 # Тесты (e2e, модульные)
```

## Структура модуля

Каждый модуль следует похожей многослойной структуре:

```
module/
├── adapters/                  # Слой адаптеров
│   └── api/
│       ├── router.py          # Определения маршрутов API (эндпоинты)
│       └── schemas.py         # Pydantic-схемы для валидации и сериализации
│
├── application/               # Слой приложения, реализующий бизнес-процессы
│   ├── commands.py            # Обработчики команд (изменение состояния)
│   ├── queries.py             # Обработчики запросов (чтение данных)
│   └── services.py            # Сервисный слой, координирующий логику приложения
│
├── domain/                    # Ядро домена, содержащее бизнес-правила и логику
│   ├── entities.py            # Доменные сущности
│   ├── events.py              # Доменные события (для event-driven архитектуры)
│   ├── exceptions.py          # Исключения, специфичные для домена
│   ├── repositories.py        # Интерфейсы репозиториев
│   ├── services.py            # Доменные сервисы
│   └── value_objects.py       # Объекты-значения
│
├── infrastructure/            # Слой инфраструктуры
│   ├── event_handlers.py      # Обработчики доменных событий
│   ├── orm/                   
│   │   └── models.py          # Модели SQLAlchemy для хранения данных
│   └── repositories/          # Реализации репозиториев
│       └── {module_name}_repository.py # Конкретная реализация репозитория
│
└── provider.py                # Провайдер DI
```

## Ключевые модули

- **Users**: Управление пользователями
- **Auth**: Аутентификация и токены
- **Coworkings**: Управление коворкингами
- **Spots**: Управление рабочими местами
- **Bookings**: Бронирование мест
- **Notifications**: Уведомления пользователей
- **Options**: Дополнительные опции
- **Storage**: Хранение файлов

## Структура базы данных

```mermaid
erDiagram
    users ||--o{ bookings : makes
    users ||--o{ device_tokens : has
    users ||--o{ notifications : receives
    
    coworkings ||--o{ spots : contains
    coworkings ||--o{ options : offers
    
    spots ||--o{ bookings : booked_for
    
    bookings }o--o{ options : has
    
    users {
        uuid id PK
        string email
        string full_name
        string hashed_password
        boolean is_business
        boolean is_banned
        string avatar_url
    }

    device_tokens {
        uuid id PK
        uuid user_id FK
        string token
        string device_type "android/ios/web"
        datetime created_at
        datetime updated_at
    }

    notifications {
        uuid id PK
        uuid user_id FK
        enum type
        string title
        string body
        json data
        datetime created_at
        datetime read_at
    }

    coworkings {
        uuid id PK
        string name
        string description
        string address
        time opens_at
        time closes_at
        string[] images
    }

    spots {
        uuid id PK
        uuid coworking_id FK
        string name
        string description
        integer position
        string status "active/inactive"
    }

    options {
        uuid id PK
        uuid coworking_id FK
        string name
    }

    bookings {
        uuid id PK
        uuid user_id FK
        uuid spot_id FK
        datetime time_from
        datetime time_until
        string status "active/cancelled/expired"
        uuid[] options
    }
```

## Поток взаимодействия сервисов

### Бронирование места

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant BookingService
    participant SpotService
    participant DB
    participant EventBus
    participant NotificationService

    Client->>API: GET /coworkings/{id}/spots?time_from=X&time_until=Y
    API->>SpotService: get_spots_with_status()
    SpotService->>DB: Получить места
    SpotService->>BookingService: Проверить доступность
    API->>Client: 200 OK (места с информацией о доступности)

    Client->>API: POST /bookings (spot_id, time_from, time_until)
    API->>BookingService: create_booking()
    BookingService->>DB: Проверить существование места
    BookingService->>BookingService: Проверить на пересечение бронирований
    BookingService->>DB: Создать бронирование
    BookingService->>EventBus: Опубликовать событие BookingCreated
    EventBus->>NotificationService: Отправить подтверждение бронирования
    API->>Client: 201 Created (детали бронирования)
```


## Архитектура развертывания

```mermaid
flowchart TD
    A[Nginx] --> B[API Server]
    A --> C[Grafana]
    B --> D[PostgreSQL]
    B --> E[RabbitMQ]
    F[Runner] --> D
    F --> E
    G[Prometheus] --> B
    G --> E
    H[Loki] --> I[Logging Collection]
    C --> G
    C --> H
```

## Внедрение зависимостей

```mermaid
flowchart TD
    A[Container] --> B[Config Provider]
    A --> C[Database Provider]
    A --> D[Event Bus Provider]
    
    C --> F[AsyncEngine]
    C --> G[AsyncSessionMaker]
    
    J[Service Providers] --> K[UserProvider]
    J --> L[AuthProvider]
    J --> M[BookingProvider]
    
    K --> O[UserRepository]
    K --> P[UserService]
```

## Общая схема компонентов

```mermaid
flowchart TD
    classDef client fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef proxy fill:#f5d6c6,stroke:#333,stroke-width:1px
    classDef app fill:#c2e0f4,stroke:#333,stroke-width:1px
    classDef db fill:#d4f4c2,stroke:#333,stroke-width:1px
    classDef messaging fill:#f4e3c2,stroke:#333,stroke-width:1px
    classDef monitoring fill:#e1c2f4,stroke:#333,stroke-width:1px

    client[Клиент]:::client
    
    subgraph "Внешний периметр"
        nginx[Nginx Reverse Proxy SSL-терминация]:::proxy
    end
    
    subgraph "Приложение"
        server[Server FastAPI]:::app
        runner[Background Runner]:::app
    end
    
    subgraph "Хранение данных"
        postgres[(PostgreSQL)]:::db
        rabbitmq[RabbitMQ Сообщения]:::messaging
    end
    
    subgraph "Мониторинг и логирование"
        prometheus[Prometheus Сбор метрик]:::monitoring
        grafana[Grafana Дашборды]:::monitoring
        loki[Loki Логи]:::monitoring
    end
    
    client -->|HTTPS| nginx
    nginx -->|/api| server
    nginx -->|/grafana| grafana
    
    server <-->|SQL| postgres
    server -->|Publish| rabbitmq
    runner -->|Consume| rabbitmq
    runner <-->|SQL| postgres
    
    prometheus -->|Scrape metrics| server
    prometheus -->|Scrape metrics| rabbitmq
    prometheus -->|Scrape metrics| loki
    
    server & runner & postgres & rabbitmq & nginx -->|Logs| loki
    
    grafana -->|Query| prometheus
    grafana -->|Query| loki
    
    style nginx stroke-dasharray: 5 5
```

## Сетевая архитектура

```mermaid
flowchart LR
    classDef nginx fill:#f5d6c6,stroke:#333,stroke-width:1px
    classDef main fill:#c2e0f4,stroke:#333,stroke-width:1px
    classDef loki fill:#e1c2f4,stroke:#333,stroke-width:1px
    classDef prom fill:#f4e3c2,stroke:#333,stroke-width:1px
    
    subgraph nginx-net["nginx-net (Внешний доступ)"]
        nginx[Nginx 80/443]:::nginx
        serverFront[Server 8080]:::main
        grafanaFront[Grafana 3000]:::loki
    end
    
    subgraph main-net["main-net (Основные сервисы)"]
        direction TB
        serverBack[Server]:::main
        runner[Runner]:::main
        postgres[(PostgreSQL 5432)]:::main
        rabbitmq[(RabbitMQ 5672/15672/15692)]:::main
    end
    
    subgraph loki-net["loki-net (Логирование)"]
        loki[Loki 3100]:::loki
        grafanaLoki[Grafana]:::loki
    end
    
    subgraph prometheus-net["prometheus-net (Мониторинг)"]
        prometheus[Prometheus 9090]:::prom
        grafanaProm[Grafana]:::prom
    end
    
    nginx -.->|Proxy| serverFront
    nginx -.->|Proxy| grafanaFront
    
    serverFront ===|Same container| serverBack
    grafanaFront ===|Same container| grafanaLoki
    grafanaFront ===|Same container| grafanaProm
    
    serverBack <--->|SQL| postgres
    serverBack <--->|AMQP| rabbitmq
    runner <--->|SQL| postgres
    runner <--->|AMQP| rabbitmq
    
    prometheus -->|Scrape| serverBack
    prometheus -->|Scrape| rabbitmq
    prometheus -->|Scrape| loki
    
    loki <-.->|Log collection| main-net
    loki <-.->|Log collection| nginx
```

## CI/CD и безопасность

```mermaid
flowchart LR
    classDef application fill:#d4f1c5,stroke:#333,stroke-width:1px
    classDef infrastructure fill:#c2e0f4,stroke:#333,stroke-width:1px
    classDef security fill:#f4e3c2,stroke:#333,stroke-width:1px
    classDef monitoring fill:#f1c5e7,stroke:#333,stroke-width:1px
    classDef cicd fill:#e0c2f4,stroke:#333,stroke-width:1px

    subgraph "Application Services"
        server[Server API]:::application
        runner[Background Runner]:::application
    end

    subgraph "Infrastructure"
        postgres[PostgreSQL DB]:::infrastructure
        rabbitmq[RabbitMQ]:::infrastructure
    end

    subgraph "Monitoring"
        prometheus[Prometheus]:::monitoring
        grafana[Grafana]:::monitoring
        loki[Loki Logging]:::monitoring
    end
    
    subgraph "Security"
        nginx[Nginx Reverse Proxy]:::security
        ssl[TLS 1.3 / Let's Encrypt]:::security
    end
    
    subgraph "CI/CD Pipeline"
        gitlab[GitLab Repository]:::cicd
        ci[GitLab CI/CD]:::cicd
        deployJob[Deploy SSH/rsync]:::cicd
        docker[Docker Compose Profiles]:::cicd
    end

    %% Application connections
    server <--> postgres
    server <--> rabbitmq
    runner <--> postgres
    runner <--> rabbitmq

    %% Monitoring connections
    loki --> grafana
    prometheus --> grafana
    server --> prometheus
    rabbitmq --> prometheus
    loki -.-> docker

    %% Security flow
    nginx --> server
    nginx --> grafana
    ssl --> nginx

    %% CI/CD flow
    gitlab --> ci
    ci --> deployJob
    deployJob --> docker
    docker --> server
    docker --> runner
    docker --> nginx
    docker --> loki
    docker --> prometheus
    docker --> grafana
    docker --> postgres
    docker --> rabbitmq

    %% External connections
    client([External Client]) --> nginx
```

## API документация

### OpenAPI спецификация
Полная OpenAPI спецификация доступна по ссылке: https://prod-team-41-l4fbsnm0.REDACTED/api/openapi.json

### Swagger UI
Swagger UI: https://prod-team-41-l4fbsnm0.REDACTED/api/docs/

### Работа со Swagger UI

#### Аутентификация
Для авторизованных запросов используйте JWT токен:

1. Получите токен через эндпоинт `/auth/login`, отправив email и пароль
2. Используйте полученный токен в разделе "Authorize" (кнопка в правом верхнем углу Swagger UI)
3. Введите токен в форму

#### Примеры запросов

##### Создание пользователя
```json
{
  "email": "user@example.com",
  "full_name": "Test User",
  "password": "password123",
  "is_business": false
}
```

## Тестирование


## CI/CD Pipeline

