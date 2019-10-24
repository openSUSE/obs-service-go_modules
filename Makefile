prefix = /usr

servicedir = ${prefix}/lib/obs/service

default:

install:
	install -d $(DESTDIR)$(servicedir)
	install -m 0755 go_modules $(DESTDIR)$(servicedir)
	install -m 0644 go_modules.service $(DESTDIR)$(servicedir)

.PHONY: default install 
