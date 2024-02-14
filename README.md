# Stand updater

## Для чего нужен проект?
Что бы автоматически запускать gitlab джобы, дожидаться поднятия пода в кубере и затем применять миграции.

## Интерфейс

![Alt Text](https://github.com/psvoropaev/stand_updater/blob/first_vision/media/interface.gif?raw=true)

## Запуск
Должен быть сконфигурирован кубер конфиг `~/.kube/config`, и указаны переменные окружения для работы с гитлаб:
```bash
export GITLAB_URL=https://some_gitlab.com
export GITLAB_PRIVATE_TOKEN=<some_gitlab_private_token>
```
### Команда для запуска
```bash
python updater.py -n <namespace name>
```

## Конфигурация проектов
Конфиги проектов хранятся в файле `config/project.yml`

```yaml
    -   name: <gitlab project name>
        group: <gitlab group name>
        target:
            type: branch | commit | tag
            id: <branch_name> | <commit short or long hash> | <tag_name>
        pod:
            migration: [ Optional ] alembic | django
            k8s_label_selector: "<k8s pod label>=<value>,<k8s pod label>=<value>,..."
        keywords: [ Optional ] list of keywords that can be in the gitlab job state. 
            - ps
            - deploy
```
`k8s_label_selector` поле нужно для поиска нужного пода в k8s, если найдено несколько подов, то будет использован первый для миграций.

`keywords` поле нужно, что бы найти нужную джобу для запуска в срезе неймспейса и проекта.