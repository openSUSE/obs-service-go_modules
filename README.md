# OBS Source Service `obs-service-go_modules`

This is the git repository for
[`devel:languages:go/obs-service-go_modules`](https://build.opensuse.org/package/show/devel:languages:go/obs-service-go_modules),
an [Open Build Service (OBS)](https://build.opensuse.org)
[Source Service](https://openbuildservice.org/help/manuals/obs-user-guide/cha.obs.source_service.html)
to download, verify, and vendor Go module dependency sources.
The authoritative source is https://github.com/openSUSE/obs-service-go_modules.

Using
[`go.mod` and `go.sum`](https://github.com/golang/go/wiki/Modules)
present in a Go application,
`obs-service-go_modules` will call Go tools in sequence:

```
go mod download
go mod verify
go mod vendor
```

`obs-service-go_modules` will create a `vendor.tar[.<tar compression>]` archive
containing the `vendor/` directory populated by `go mod vendor`. The archive
is generated in the rpm package directory, and can be committed to
[OBS](https://build.opensuse.org) to facilitate offline Go application package builds
for [openSUSE](https://www.opensuse.org),
[SUSE](https://www.suse.com), and numerous other distributions.

## Usage for packagers

Presently it is assumed the Go application is distributed as a tarball named
`app-0.1.0.tar[.<tar compression>]`, unpacking to `app-0.1.0/`.
The `<tar compression>` extension can be specified using the `compression` parameter,
and defaults to `gz`.
`obs-service-go_modules` will autodetect tarball archives of the form `app-0.1.0.tar[.<tar compression>]`,
where the RPM packaging uses spec file `app.spec`.

Create a `_service` file containing:

```
<services>
  <service name="go_modules" mode="disabled">
  </service>
</services>
```

The archive name can alternatively be specified using service parameter `archive`.

Run `osc` command locally:

```
osc service disabledrun
```

See [Example](#example) below for typical output with a complete `_service` file.

## Building Go applications with vendored dependency modules

Go commands support building with vendored dependencies,
but it is no longer on by default.
Upstream has stated vendoring is not going away.
To ensure the top-level `vendor/` directory is used by go build, either:

- pass the argument `go build -mod=vendor` to each invocation

- set environment variable `GOFLAGS=-mod=vendor` to apply the setting to all invocations

More information about additional controls is available at:
[Go Module Knobs](https://github.com/thepudds/go-module-knobs/blob/master/README.md),
[Go Wiki: Modules: How do I use vendoring](https://github.com/golang/go/wiki/Modules#how-do-i-use-vendoring-with-modules-is-vendoring-going-away) and
[Go Wiki: Modules: Old vs. new behavior](https://github.com/golang/go/wiki/Modules#when-do-i-get-old-behavior-vs-new-module-based-behavior)

## Example

Using the [hugo](https://github.com/gohugoio) static site generator as
an example of a Go application with a large number of Go module
dependencies, `obs-service-go_modules` produces `vendor.tar.gz`:

```
$ ls -1
hugo-0.57.2.tar.gz
hugo.changes
hugo.spec
_service
_servicedata

$ osc service disabledrun
INFO:obs-service-go_modules:Autodetecting archive since no archive param provided in _service
INFO:obs-service-go_modules:Archive autodetected at /path/to/prj/pkg/hugo-0.57.2.tar.gz
INFO:obs-service-go_modules:Using archive hugo-0.57.2.tar.gz
INFO:obs-service-go_modules:Extracting hugo-0.57.2.tar.gz to /path/to/tmpdir
INFO:obs-service-go_modules:Using go.mod found at /path/to/tmpdir/hugo-0.57.2/go.mod
INFO:obs-service-go_modules:go mod download
go: finding cloud.google.com/go v0.39.0
go: finding contrib.go.opencensus.io/exporter/aws v0.0.0-20181029163544-2befc13012d0
go: finding contrib.go.opencensus.io/exporter/ocagent v0.4.12
go: finding contrib.go.opencensus.io/exporter/stackdriver v0.11.0
go: finding contrib.go.opencensus.io/integrations/ocsql v0.1.4
go: finding contrib.go.opencensus.io/resource v0.0.0-20190131005048-21591786a5e0
go: finding github.com/Azure/azure-amqp-common-go v1.1.4
go: finding github.com/Azure/azure-pipeline-go v0.1.9
go: finding github.com/Azure/azure-sdk-for-go v27.3.0+incompatible
(elided: 193 additional entries)
go: finding gopkg.in/fsnotify.v1 v1.4.7
go: finding gopkg.in/resty.v1 v1.12.0
go: finding gopkg.in/tomb.v1 v1.0.0-20141024135613-dd632973f1e7
go: finding gopkg.in/yaml.v2 v2.2.2
go: finding honnef.co/go/tools v0.0.0-20190106161140-3f1c8253044a
go: finding pack.ag/amqp v0.11.0
INFO:obs-service-go_modules:go mod verify
INFO:obs-service-go_modules:all modules verified
INFO:obs-service-go_modules:go mod vendor
INFO:obs-service-go_modules:Vendor go.mod dependencies to vendor.tar.gz

$ ls -1
hugo-0.57.2.tar.gz
hugo.changes
hugo.spec
_service
_servicedata
vendor.tar.gz
```

## Example `_service` configuration

OBS Source Services
[`obs-service-tar_scm`](https://github.com/openSUSE/obs-service-tar_scm),
[`obs-service-set_version`](https://github.com/openSUSE/obs-service-set_version) and
[`obs-service-recompress`]()
can be used together to automate Go application source archive handling and support local development workflows:

```
<services>
  <service name="tar_scm" mode="disabled">
    <param name="url">git://github.com/gohugoio/hugo.git</param>
    <param name="scm">git</param>
    <param name="exclude">.git</param>
    <param name="revision">v0.57.2</param>
    <param name="versionformat">@PARENT_TAG@</param>
    <param name="changesgenerate">enable</param>
    <param name="versionrewrite-pattern">v(.*)</param>
  </service>
  <service name="set_version" mode="disabled">
    <param name="basename">hugo</param>
  </service>
  <service name="recompress" mode="disabled">
    <param name="file">*.tar</param>
    <param name="compression">gz</param>
  </service>
  <service name="go_modules" mode="disabled">
  </service>
</services>
```

Persistent state for changelog generation is stored in `_servicedata`.

## Transition note

Until such time as `obs-service-go_modules` is available on
[OBS](https://build.opensuse.org), `vendor.tar[.<tar compression>]` should
be committed along with the Go application release tarball.

## openSUSE RPM packages built using `obs-service-go_modules`

- [hugo](https://build.opensuse.org/package/show/devel:languages:go/hugo)
- [go-modiff](https://build.opensuse.org/package/show/devel:languages:go/go-modiff)
- [gohack](https://build.opensuse.org/package/show/devel:languages:go/gohack)
- [mod](https://build.opensuse.org/package/show/devel:languages:go/mod)
- [mgit](https://build.opensuse.org/package/show/devel:languages:go/mgit)

## FAQ

### Q: Does `vendor.tar[.<tar compression>]` need to be committed to OBS package?

A: Currently yes.
As long as  `obs-service-go_modules` is run locally via `osc service disabledrun`,
then `vendor.tar[.<tar compression>]` should be committed and referenced as an additional `Source:`.
If and when `obs-service-go_modules` is available on
[OBS](https://build.opensuse.org),
additional strategies should be possible such as a `vendor.cpio`
where the vendored dependencies are managed on the fly
and will not need to be committed to OBS package revisions.
The single source of truth `go.mod` and `go.sum` always remain with the application source code.

### Q: Does `obs-service-go_modules` update dependencies to newer versions?

A: No. Go modules use
[Minimum Version Selection](https://github.com/golang/go/wiki/Modules#faqs--minimal-version-selection),
selecting the minimum (oldest) version of a Go module that satisfies all `go.mod` entries in the transitive dependency set.
Go modules are relatively new and real-world use remains to be seen,
but the expectation is that dependency versions will increment at a measured pace
driven by upstream projects making releases with a well-tested dependency set.
It is a design goal that there should be no surprise updates pulled in,
and the dependency set selected remains repeatable over time.
These characteristics should be quite favorable for distribution packagers.

### Q: Does `obs-service-go_modules` cache Go module downloads to save time and bandwidth?

A: Yes. For local use with `osc service disabledrun`,
`obs-service-go_modules` uses the standard module cache `~/go/pkg/mod`.
Subsequent runs of `obs-service-go_modules` with a populated cache will finish in less time.

### Q: Would `obs-service-go_modules` installed on OBS cache Go module downloads to conserve server resources?

A: Not directly.
The Go module cache `~/go/pkg/mod` would not persist between OBS build runs.
Running a private [Go proxy](https://proxy.golang.org) inside OBS could accomplish this,
as well as provide protections against third-party service outages and
upstream Go modules being removed by the author.

## License

GNU General Public License v2.0 or later
