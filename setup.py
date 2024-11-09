from setuptools import setup, find_packages

setup(
    name="mfrc522",
    version="1.0.0",
    author="Damian Cyrana",
    description="MFRC522 RFID reader library for MicroPython on Raspberry Pi Pico",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/damiancyrana/mfrc522_micropython",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "machine",  # Note: 'machine' is typically provided by the hardware and MicroPython environment
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Home Automation",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
