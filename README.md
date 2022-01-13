# healthchecksio-check-k8s-operator

A kubernetes operator to manage healthchecks.io checks as kubernetes objects.

Written using [kopf](https://kopf.readthedocs.io/en/stable/) and [py-healthchecks.io](https://github.com/andrewthetechie/py-healthchecks.io)

## Features

-   Supports self-hosted or saas healthchecks.io instances.
-   Can Create, Update, and Delete checks.
-   Supports Healthchecks.io SAAS and self-hosted instances

## Requirements

-   helm
-   kubernetes 1.19+
-   A healthchecks.io api key

## Installation

You can install the operator via helm.

First, define a secret with your healthchecks.io API key. If you are using a self-hosted instance, add your API URL to the secret too in the format "http(s)://yourinstancedomain.com/api/"

You will need to add these values to a values.yaml. If you named your secret "hcio-secret" and put your API key as a API_KEY and your api url as URL, your values.yaml would look as below.

```
secret:
  name: "hcio-secret"
  api_key: API_KEY
  url_key: URL
```

> **_NOTE:_**  Make sure to setup this secret in the same namespace you plan to install the operator

> **_NOTE:_**  If you're using healthcheks.io saas, leave the url_key blank.

Now, you're ready to install the operator via helm. This will install the operator, a service account, and the CRD

``` console
$ helm repo add andrewthetechie https://andrewthetechie.github.io/healthchecksio-check-k8s-operator/
$ helm repo update
$ helm install (--namespace yournamespace --create-namespace) hcio-operator andrewthetechie/hcio-check-operator -f values.yaml
```

You can then check to see if the operator is running properly by looking for a pod in your namespace and checking for the crd

```
$ kubectl get pods --namespace yournamespace
NAME                                                 READY   STATUS    RESTARTS   AGE
hcio-operator-hcio-check-operator-557b5cfc74-6zs5w   1/1     Running   0          30s
$ kubectl get crds
NAME                     CREATED AT
checks.healthchecks.io   2022-01-13T04:15:44Z
```

## Creating a check

Once the operator and crd are installed, you can create a check by adding a kubernetes object. The only required value for a new check is a name

```
apiVersion: healthchecks.io/v1
kind: Check
metadata:
  name: test-check
spec: {}
```

You can use any key/value in the [healthchecks.io create check api](https://healthchecks.io/docs/api/#create-check) in your spec. The [CRD](./charts/templates/crd.yml) also has a spec you can look at to craft your check.

```
$ kubectl apply -f test-check.yaml
check.healthchecks.io/test-check created
$ kubectl get checks
NAME         UUID                                   AGE
test-check   313d57cc-5340-4cf8-ae3e-6f149e900c87   38s
$ kubectl describe check test-check
Name:         test-check
Namespace:    test
Labels:       <none>
Annotations:  kopf.zalando.org/last-handled-configuration: {"spec":{"grace":3600,"manual_resume":false,"methods":"","timeout":86400,"tz":"UTC"}}
API Version:  healthchecks.io/v1
Kind:         Check
Metadata:
  Creation Timestamp:  2022-01-13T04:38:07Z
  Finalizers:
    kopf.zalando.org/KopfFinalizerMarker
  Generation:  2
  Resource Version:  3015
  UID:               9c1109d8-e7b8-45a3-b9b8-21f170308e9e
Spec:
  Grace:          3600
  manual_resume:  false
  Methods:        
  Timeout:        86400
  Tz:             UTC
Status:
  Channels:       
  create_fn:      Success
  Desc:           
  Grace:          3600
  manual_resume:  false
  Methods:        
  n_pings:        0
  Name:           test-check
  pause_url:      healthchecks.io/api/v1/checks/313d57cc-5340-4cf8-ae3e-6f149e900c87/pause
  ping_url:       healthchecks.io/ping/313d57cc-5340-4cf8-ae3e-6f149e900c87
  Slug:           test-check
  Status:         new
  Tags:           
  Timeout:        86400
  update_url:     healthchecks.io/api/v1/checks/313d57cc-5340-4cf8-ae3e-6f149e900c87
  Uuid:           313d57cc-5340-4cf8-ae3e-6f149e900c87
Events:
  Type    Reason   Age   From  Message
  ----    ------   ----  ----  -------
  Normal  Logging  51s   kopf  Creation is processed: 1 succeeded; 0 failed.
  Normal  Logging  51s   kopf  Handler 'create_fn' succeeded.
```

## Contributing

Contributions are very welcome. To learn more, see the [Contributor
Guide](CONTRIBUTING.md).

## License

Distributed under the terms of the [MIT
license](https://opensource.org/licenses/MIT)

## Issues

If you encounter any problems, please [file an
issue](https://github.com/andrewthetechie/healthchecksio-check-k8s-operator/issues)
along with a detailed description.
