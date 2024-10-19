# How to use this doit flow for SC3 project

_Assume the following paths and git branches_

- `$WORKING_DIR/alloy-apps`: _master_ branch
- `$WORKING_DIR/alloy-gem5`: _sc3_ branch

- Build apps

```
$ cd alloy-apps/doit-flows
$
$ # build cilk5 apps and make gem5 links to binaries
$ doit -n64 make-gem5-links-cilk5
$ # build ligra apps and make gem5 links to binaries
$ doit -n64 make-gem5-links-ligra
$
$ # make gem5 app dictionary
$ doit make-gem5-dict-cilk5
$ doit make-gem5-dict-ligra
```

- gem5 (MESI baseline)

```
$ cd $WORKING_DIR/alloy-gem5
$ cd doit-flows/sc3
$ doit -n64 sim-mesi
```
