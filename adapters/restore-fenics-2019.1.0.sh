#!/usr/bin/env bash

deb_download_dir="fenics_deb_files/"
mkdir -p "${deb_download_dir}"

files=("dolfin-bin_2019.1.0-1~ppa1~bionic4_all.deb"
  "dolfin-doc_2019.1.0-1~ppa1~bionic4_all.deb"
  "libdolfin-dev_2019.1.0-1~ppa1~bionic4_amd64.deb"
  "libdolfin2019.1_2019.1.0-1~ppa1~bionic4_amd64.deb"
  "python-dolfin_2019.1.0-1~ppa1~bionic4_all.deb"
  "python3-dolfin_2019.1.0-1~ppa1~bionic4_amd64.deb"
  )
base_url="https://launchpad.net/~fenics-packages/+archive/ubuntu/fenics/+build/18158564/+files/"
#echo "${files[@]}"
for deb_file in "${files[@]}"
do
  if [ ! -f "./${deb_download_dir}${deb_file}" ]; then
    echo "Download ${deb_file}"
    wget -N "${base_url}/${deb_file}" --directory-prefix="${deb_download_dir}"
  fi
done

files=("fenics_2019.1.0.1~ppa1~bionic1_amd64.deb")
base_url="https://launchpad.net/~fenics-packages/+archive/ubuntu/fenics/+build/16702224/+files/"
for deb_file in "${files[@]}"
do
  if [ ! -f "./${deb_download_dir}${deb_file}" ]; then
    echo "Download ${deb_file}"
    wget -N "${base_url}/${deb_file}" --directory-prefix="${deb_download_dir}"
  fi
done

files=("python-fiat_2019.1.0-1~ppa1~bionic1_all.deb"
  "python3-fiat_2019.1.0-1~ppa1~bionic1_all.deb"
  )
base_url="https://launchpad.net/~fenics-packages/+archive/ubuntu/fenics/+build/16701565/+files/"
for deb_file in "${files[@]}"
do
  if [ ! -f "./${deb_download_dir}${deb_file}" ]; then
    echo "Download ${deb_file}"
    wget -N "${base_url}/${deb_file}" --directory-prefix="${deb_download_dir}"
  fi
done


files=("python-ufl-doc_2019.1.0-1~ppa1~bionic1_all.deb"
  "python-ufl_2019.1.0-1~ppa1~bionic1_all.deb"
  "python3-ufl_2019.1.0-1~ppa1~bionic1_all.deb"
  )
base_url="https://launchpad.net/~fenics-packages/+archive/ubuntu/fenics/+build/16701566/+files/"
for deb_file in "${files[@]}"
do
  if [ ! -f "./${deb_download_dir}${deb_file}" ]; then
    echo "Download ${deb_file}"
    wget -N "${base_url}/${deb_file}" --directory-prefix="${deb_download_dir}"
  fi
done

files=( "python-dijitso_2019.1.0-1~ppa1~bionic1_all.deb"
  "python3-dijitso_2019.1.0-1~ppa1~bionic1_all.deb"
  )
base_url="https://launchpad.net/~fenics-packages/+archive/ubuntu/fenics/+build/16701563/+files/"
for deb_file in "${files[@]}"
do
  if [ ! -f "./${deb_download_dir}${deb_file}" ]; then
    echo "Download ${deb_file}"
    wget -N "${base_url}/${deb_file}" --directory-prefix="${deb_download_dir}"
  fi
done

files=( "python-ffc_2019.1.0.post0-1~ppa1~bionic1_all.deb"
  "python3-ffc_2019.1.0.post0-1~ppa1~bionic1_all.deb"
  )
base_url="https://launchpad.net/~fenics-packages/+archive/ubuntu/fenics/+build/16701564/+files/"
for deb_file in "${files[@]}"
do
  if [ ! -f "./${deb_download_dir}${deb_file}" ]; then
    echo "Download ${deb_file}"
    wget -N "${base_url}/${deb_file}" --directory-prefix="${deb_download_dir}"
  fi
done

files=( "libmshr-dev_2019.1.0+full1-1~ppa1~bionic1_amd64.deb"
  "libmshr2019.1_2019.1.0+full1-1~ppa1~bionic1_amd64.deb"
  "python3-mshr_2019.1.0+full1-1~ppa1~bionic1_amd64.deb"
  )
base_url="https://launchpad.net/~fenics-packages/+archive/ubuntu/fenics/+build/16702222/+files/"
for deb_file in "${files[@]}"
do
  if [ ! -f "./${deb_download_dir}${deb_file}" ]; then
    echo "Download ${deb_file}"
    wget -N "${base_url}/${deb_file}" --directory-prefix="${deb_download_dir}"
  fi
done

echo "Remove all the old fenics stuff"
#apt install "./${files[@]}"
apt --fix-broken install
pkg_to_remove=("fenics"
  "libdolfin2019.2"
  "python-dolfin"
  "python3-dolfin"
  "dolfin-doc"
  "dolfin-bin"
  "libdolfin-dev"
  "libdolfin-dev-common"
  "python3-fiat"
  "python-fiat"
  "python-ufl-doc"
  "python3-ufl"
  "python-dijitso"
  "python3-dijitso"
  "python3-dolfin-real"
  "python3-mshr-real"
  "python3-mshr"
  "libmshr-dev"
  "libmshr-dev-common"
  "libdolfin2019.2"
  "libmshr2019.2"
)
apt-get remove -y python3-mshr-real python3-dolfin-real

apt purge -y fenics
#apt-get purge $(apt-cache depends <PACKAGENAME> | awk '{ print $2 }' | tr '\n' ' ')
for pkg in "${pkg_to_remove[@]}"
do
  echo "Removing ${pkg}"
  #apt-get remove "${pkg}"
  apt-get purge -y "${pkg}"
done


echo "Installing FEniCS 2019.1.0 packages"
cd "${deb_download_dir}"

#apt-get remove fenics libdolfin2019.2 python-dolfin python3-dolfin dolfin-doc dolfin-bin libdolfin-dev libdolfin-dev-common python3-fiat python-fiat python-ufl-doc python-3-ufl  python-dijitso python3-dijitso
#apt-get remove python3-dolfin-real
#apt-get
#dpkg -i "${files[@]}"
ls -l
dpkg -i *.deb
dpkg --configure -a
#apt install -f
apt-get autoremove
