---
title: "Nostalgia del M2M"
date: 2026-02-08
categories: [technology]
tags: [agro, iot, fluxrig, strategy, m2m, aiu, punta-tech, embedded, linux, zephyr]
lang: es
layout: post
toc: false
image:
  path: /assets/img/posts/2026-02-07-agro-en-punta/cover.jpg
  alt: "Agro en Punta"
---

Una de las primeras empresas que inicié fue **Edantech**, que tenía foco en el **[Machine to Machine (M2M)](https://www.gartner.com/en/information-technology/glossary/machine-to-machine-m2m-communications)**, término que luego evolucionó a llamarse **[Internet of Things (IoT)](https://www.gartner.com/en/information-technology/glossary/internet-of-things)**.

> [Enlace a charla del ciclo emprendedores en red de la ORT sobre Edantech en 2010](https://facs.ort.edu.uy/66341/36/charla-del-ciclo-emprendedores-en-red.html)

Hace +20 años, mucho antes de que Starlink democratizara la conectividad global, ya estaba participando en desafíos que resolvían problemas de telemetría crítica en condiciones adversas.

*   **ActiHome:** En mi etapa en IPCom, lideré el proyecto **ActiHome**. Lejos de la domótica tradicional, fue un despliegue de **IoT a escala** en las favelas de Río de Janeiro, diseñado para combatir el hurto de energía mediante sistemas de pre-pago. Una iniciativa que fue destacada por la prensa como *"software uruguayo de punta triunfa en países emergentes"*.
    
    > [Leer nota en El País](https://www.elpais.com.uy/el-empresario/software-uruguayo-de-punta-triunfa-en-paises-emergentes)

    <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: stretch;">
      <div style="flex: 1 1 300px; display: flex; flex-direction: column; gap: 10px;">
        <img src="/assets/img/posts/2026-02-07-agro-en-punta/actihome_1.jpg" alt="ActiHome 1" style="width: 100%; height: auto; object-fit: cover;">
        <img src="/assets/img/posts/2026-02-07-agro-en-punta/actihome_3.jpg" alt="ActiHome 3" style="width: 100%; height: auto; object-fit: cover;">
      </div>
      <div style="flex: 1 1 300px; display: flex;">
        <img src="/assets/img/posts/2026-02-07-agro-en-punta/actihome_2.jpg" alt="ActiHome 2" style="width: 100%; object-fit: cover;">
      </div>
    </div>

*   **Medición Satelital (2007):** Implementé sistemas de medición y corte remoto de energía eléctrica utilizando la constelación de satélites de órbita baja [Orbcomm](https://www.orbcomm.com/). El ancho de banda era mínimo y la latencia alta, lo que exigió diseñar protocolos binarios eficientes, una escuela que hoy aplico en FluxRig.

    **[Ver slide de la época en mi presentación de Elastic](/es/posts/elastic-montevideo-meetup/#slide-7)**

    ![Slide 07 - M2M Origins](/assets/img/posts/2019-11-13-elastic-meetup/slides/slide-07.jpg)

    <div class="row">
      <div class="col-md-6">
        <img src="/assets/img/posts/2026-02-07-agro-en-punta/m2m_1.jpg" alt="Edantech M2M">
      </div>
      <div class="col-md-6">
        <img src="/assets/img/posts/2026-02-07-agro-en-punta/m2m_2.jpg" alt="Edantech M2M Board">
      </div>
    </div>

*   **Telemática Automotriz:** Diseño/fabricación de rastreadores GPS para vehículos, y desarrollo de herramientas para la validación del protocolo **[ACP245](https://github.com/andresantoniuk/acp245)**, utilizadas por actores relevantes de la industria. Un proyecto que contó oportunamente con el apoyo de  [ORT/FOCEM](https://fi.ort.edu.uy/54864/33/proyecto-de-alto-contenido-tecnologico-presentado-por-graduado-es-cofinanciado-por-el-focem.html).


## Conexión con el presente: De Amsterdam a Punta del Este

Esa nostalgia del M2M y Embedded Linux me picó el "bichito" hace pocos meses, cuando viajé al **[Open Source Summit Europe]({% post_url 2025-09-09-techevents-europe-2025 %})** y recorrí la zona de **[Zephyr](https://www.zephyrproject.org/)** en la exposición.

<div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: stretch; margin-bottom: 20px;">
  <div style="flex: 1 1 300px;">
    <img src="/assets/img/posts/2026-02-07-agro-en-punta/oss_amsterdam_2025_1.jpg" alt="OSS Amsterdam 1" style="width: 100%; height: 480px; object-fit: cover;">
  </div>
  <div style="flex: 1 1 300px;">
    <img src="/assets/img/posts/2026-02-07-agro-en-punta/oss_amsterdam_2025_2.jpg" alt="OSS Amsterdam 2" style="width: 100%; height: 480px; object-fit: cover;">
  </div>
</div>

Ese sentimiento conectó de inmediato con la realidad local cuando, ya de vuelta y en uno de los eventos de principios de año —el **[Tech Lunch de TRIBU](https://www.tribulatam.com/eventos/tech-lunch-tribusummit-punta-del-este-481)**—, hubo un momento que me sacó de mi zona de confort. El mensaje fue claro y contundente: **existe una desconexión real entre los "techies" y la realidad productiva del agro en Uruguay.**

Esa inquietud resonó en mí y validó conversaciones que ya venía teniendo con otros actores del ecosistema. Decidí entonces dedicar unos días a recorrer **[Agro en Punta](https://agroenpunta.com)** para conocer esa realidad de primera mano.

### Un mundo nuevo (y conocido)

Me vengo sorprendido. Es un mundo nuevo para mí, pero donde los patrones de problemas me resultan familiarmente conocidos.

Si bien vi tecnología aplicada por empresas que están haciendo un trabajo increíble para cerrar esa brecha —como **[Tu Gestion Agropecuaria](https://www.linkedin.com/company/tu-gestion-agropecuaria)**, **[Nettra](https://www.linkedin.com/company/nettra/)**, **[Rabbit](https://agro.rabbit.com.uy/es)**, **[RanchGPT](https://www.ranchgpt.com/)** y **[Digital Agro](https://www.digitalagro.org/)**—, percibí que aún hay muchísima necesidad y oportunidades.

Un concepto que se repitió en varias charlas fue la desconexión existente entre muchas de las soluciones tecnológicas propuestas y las necesidades reales de los productores.

## El Futuro es Integrado

Hoy, con **[FluxRig](https://jaab.tech/fluxrig/)** (el orquestador de lógica de negocio), busco cerrar esa brecha. Mi objetivo es aprovechar la experiencia adquirida en ambientes de misión crítica y altamente regulados (como el sector financiero) para aplicarla a soluciones de la vida real.

No se trata solo de conectar dispositivos, sino de orquestar la lógica de negocio que da sentido a esos datos, integrando lo viejo (legacy) con lo nuevo.

Encuentro una gran sinergia entre [revivir dinosaurios](/es/posts/reviviendo-dinosaurios/) y conectar cosas del mundo real a sistemas críticos: ambos requieren la robustez de entornos donde no hay margen de error.

El agro necesita tecnología, sí. Pero sobre todo necesita tecnología que entienda su realidad, que sea robusta, eficiente y que resuelva problemas reales sin agregar fricción innecesaria, generando beneficios y rentabilidad concretos y medibles.