<?php

// Get the latest release tag of Guzzle
$version = substr(`git describe --abbrev=0 --tags`, 1);

$spec = Pearfarm_PackageSpec::create(array(Pearfarm_PackageSpec::OPT_BASEDIR => __DIR__))
    ->setName('guzzle')
    ->setChannel('guzzlephp.org/pear')
    ->setSummary('HTTP client and REST client framework')
    ->setDescription('Guzzle is a PHP 5.3+ HTTP client and framework for building RESTful web service clients')
    ->setReleaseVersion($version)
    ->setApiVersion($version)
    ->setReleaseStability('stable')
    ->setApiStability('stable')
    ->setLicense(Pearfarm_PackageSpec::LICENSE_MIT)
    ->addMaintainer('lead', 'Michael Dowling', 'mtdowling', 'mtdowling@gmail.com')
    ->addGitFiles()
    ->setDependsOnPHPVersion('5.3.2')
    ->addPackageDependency('EventDispatcher', 'pear.symfony.com')
    ->setNotes('HTTP client');